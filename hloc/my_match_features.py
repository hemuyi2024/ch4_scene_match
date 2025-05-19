import argparse
import pprint
import time
import cv2
import numpy as np
from functools import partial
from pathlib import Path
from queue import Queue
from threading import Thread
from typing import Dict, List, Optional, Tuple, Union

import h5py
import torch
from hloc.matchers.lightglue import LightGlue
from tqdm import tqdm

from . import logger, matchers
from .utils.base_model import dynamic_load
from .utils.parsers import names_to_pair, names_to_pair_old, parse_retrieval

"""
A set of standard configurations that can be directly selected from the command
line using their name. Each is a dictionary with the following entries:
    - output: the name of the match file that will be generated.
    - model: the model configuration, as passed to a feature matcher.
"""
confs = {
    "superpoint+lightglue": {
        "output": "matches-superpoint-lightglue",
        "model": {
            "name": "lightglue",
            "features": "superpoint",
        },
    },
    "disk+lightglue": {
        "output": "matches-disk-lightglue",
        "model": {
            "name": "lightglue",
            "features": "disk",
        },
    },
    "superglue": {
        "output": "matches-superglue",
        "model": {
            "name": "superglue",
            "weights": "indoor",
            "sinkhorn_iterations": 50,
        },
    },
    "superglue-fast": {
        "output": "matches-superglue-it5",
        "model": {
            "name": "superglue",
            "weights": "outdoor",
            "sinkhorn_iterations": 5,
        },
    },
    "NN-superpoint": {
        "output": "matches-NN-mutual-dist.7",
        "model": {
            "name": "nearest_neighbor",
            "do_mutual_check": True,
            "distance_threshold": 0.7,
        },
    },
    "NN-ratio": {
        "output": "matches-NN-mutual-ratio.8",
        "model": {
            "name": "nearest_neighbor",
            "do_mutual_check": True,
            "ratio_threshold": 0.8,
        },
    },
    "NN-mutual": {
        "output": "matches-NN-mutual",
        "model": {
            "name": "nearest_neighbor",
            "do_mutual_check": True,
        },
    },
    "adalam": {
        "output": "matches-adalam",
        "model": {"name": "adalam"},
    },
}


class WorkQueue:
    def __init__(self, work_fn, num_threads=1):
        self.queue = Queue(num_threads)
        self.threads = [
            Thread(target=self.thread_fn, args=(work_fn,)) for _ in range(num_threads)
        ]
        for thread in self.threads:
            thread.start()

    def join(self):
        for thread in self.threads:
            self.queue.put(None)
        for thread in self.threads:
            thread.join()

    def thread_fn(self, work_fn):
        item = self.queue.get()
        while item is not None:
            work_fn(item)
            item = self.queue.get()

    def put(self, data):
        self.queue.put(data)


class FeaturePairsDataset(torch.utils.data.Dataset):
    def __init__(self, pairs, feature_path_q, feature_path_r):
        self.pairs = pairs
        self.feature_path_q = feature_path_q
        self.feature_path_r = feature_path_r

    def __getitem__(self, idx):
        name0, name1 = self.pairs[idx]
        data = {}
        with h5py.File(self.feature_path_q, "r") as fd:
            grp = fd[name0]
            for k, v in grp.items():
                data[k + "0"] = torch.from_numpy(v.__array__()).float()
            # some matchers might expect an image but only use its size
            data["image0"] = torch.empty((1,) + tuple(grp["image_size"])[::-1])
        with h5py.File(self.feature_path_r, "r") as fd:
            grp = fd[name1]
            for k, v in grp.items():
                data[k + "1"] = torch.from_numpy(v.__array__()).float()
            data["image1"] = torch.empty((1,) + tuple(grp["image_size"])[::-1])
        return data

    def __len__(self):
        return len(self.pairs)


def writer_fn(inp, match_path):
    pair, pred = inp
    with h5py.File(str(match_path), "a", libver="latest") as fd:
        if pair in fd:
            del fd[pair]
        grp = fd.create_group(pair)
        matches = pred["matches0"][0].cpu().short().numpy()
        grp.create_dataset("matches0", data=matches)
        if "matching_scores0" in pred:
            scores = pred["matching_scores0"][0].cpu().half().numpy()
            grp.create_dataset("matching_scores0", data=scores)


def main(
    conf: Dict,
    pairs: list,
    features: Union[Path, str],
    export_dir: Optional[Path] = None,
    matches: Optional[Path] = None,
    features_ref: Optional[Path] = None,
    overwrite: bool = False,
    model: Optional[LightGlue] = None,
) -> Path:
    if isinstance(features, Path) or Path(features).exists():
        features_q = features
        if matches is None:
            raise ValueError(
                "Either provide both features and matches as Path" " or both as names."
            )
    else:
        if export_dir is None:
            raise ValueError(
                "Provide an export_dir if features is not" f" a file path: {features}."
            )
        features_q = Path(export_dir, features + ".h5")
        if matches is None:
            matches = Path(export_dir, f'{features}_{conf["output"]}_{pairs.stem}.h5')

    if features_ref is None:
        features_ref = features_q
    center_tif = match_from_paths(conf, pairs, matches, features_q, features_ref, overwrite, model)

    return center_tif


def find_unique_new_pairs(pairs_all: List[Tuple[str]], match_path: Path = None):
    """Avoid to recompute duplicates to save time."""
    pairs = set()
    for i, j in pairs_all:
        if (j, i) not in pairs:
            pairs.add((i, j))
    pairs = list(pairs)
    if match_path is not None and match_path.exists():
        with h5py.File(str(match_path), "r", libver="latest") as fd:
            pairs_filtered = []
            for i, j in pairs:
                if (
                    names_to_pair(i, j) in fd
                    or names_to_pair(j, i) in fd
                    or names_to_pair_old(i, j) in fd
                    or names_to_pair_old(j, i) in fd
                ):
                    continue
                pairs_filtered.append((i, j))
        return pairs_filtered
    return pairs


@torch.no_grad()
def match_from_paths(
    conf: Dict,
    pairs: list,
    match_path: Path,
    feature_path_q: Path,
    feature_path_ref: Path,
    overwrite: bool = False,
    model: Optional[LightGlue] = None,
) :
    logger.info(
        "Matching local features with configuration:" f"\n{pprint.pformat(conf)}"
    )

    if not feature_path_q.exists():
        raise FileNotFoundError(f"Query feature file {feature_path_q}.")
    if not feature_path_ref.exists():
        raise FileNotFoundError(f"Reference feature file {feature_path_ref}.")
    # match_path.parent.mkdir(exist_ok=True, parents=True)

    # assert pairs_path.exists(), pairs_path
    # pairs = parse_retrieval(pairs_path)
    # pairs = [(q, r) for q, rs in pairs.items() for r in rs]
    # pairs = find_unique_new_pairs(pairs, None if overwrite else match_path)
    # if len(pairs) == 0:
    #     logger.info("Skipping the matching.")
    #     return

    device = "cuda" if torch.cuda.is_available() else "cpu"
    t1 = time.time()
    model = model.eval().to(device)
    t2 = time.time()
    print(f"Model to device time: {t2 - t1}")
    t1 = time.time()
    dataset = FeaturePairsDataset(pairs, feature_path_q, feature_path_ref)
    loader = torch.utils.data.DataLoader(
        dataset, num_workers=5, batch_size=2, shuffle=False, pin_memory=True
    )
    t2 = time.time()
    print(f"Dataset time: {t2 - t1}")
    # writer_queue = WorkQueue(partial(writer_fn, match_path=match_path), 5)
    t3 = time.time()
    center_tif = None
    for idx, data in enumerate(tqdm(loader, smoothing=0.1)):
        print(f"Index: {idx}")
        t1 = time.time()
        data = {
            k: v if k.startswith("image") else v.to(device, non_blocking=True)
            for k, v in data.items()
        }
        t2 = time.time()
        print(f"Data to device time: {t2 - t1}")
        t1 = time.time()
        pred = model(data)
        t2 = time.time()
        print(f"Match time: {t2 - t1}")
        kp1 = data["keypoints0"].cpu().numpy()
        kp2 = data["keypoints1"].cpu().numpy()
        kp1 = kp1.squeeze()  # 去掉多余的维度，得到 (N, 2)
        kp2 = kp2.squeeze()

        matches =pred["matches"][0]
        matches_cpu = matches.cpu().numpy()

        pts1 = kp1[matches_cpu[:, 0]]
        pts2 = kp2[matches_cpu[:, 1]]

        H, mask = cv2.findHomography(pts1, pts2, cv2.RANSAC)
        h_uav, w_uav = 490, 490
        center_uav = np.array([[w_uav / 2, h_uav / 2]], dtype=np.float16)
        center_uav[0][1] = center_uav[0][1]
        # 将中心点坐标转换为齐次坐标
        center_uav_homogeneous = np.array([center_uav[0][0], center_uav[0][1], 1.0])  # 形状为 (3,)
        # 通过单应性矩阵进行变换
        center_tif_homogeneous = np.dot(H, center_uav_homogeneous)  # 形状为 (3,)
        # 归一化
        center_tif = center_tif_homogeneous[:2] / center_tif_homogeneous[2]  # 形状为 (2,)
        # angle = extract_rotation_angle(H)
        # print(f"旋转角度 (度): {angle}")
        # 打印结果
        # print(f"无人机图像中心点在tif的位置：{center_tif}")
        # pair = names_to_pair(*pairs[idx])
    t4 = time.time()
    print(f"Total time: {t4 - t3}")
    return center_tif
    #     writer_queue.put((pair, pred))
    # writer_queue.join()
    # logger.info("Finished exporting matches.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pairs", type=Path, required=True)
    parser.add_argument("--export_dir", type=Path)
    parser.add_argument("--features", type=str, default="feats-superpoint-n4096-r1024")
    parser.add_argument("--matches", type=Path)
    parser.add_argument(
        "--conf", type=str, default="superglue", choices=list(confs.keys())
    )
    args = parser.parse_args()
    main(confs[args.conf], args.pairs, args.features, args.export_dir)
