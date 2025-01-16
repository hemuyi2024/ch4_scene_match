# incremental_extract_retrieve.py

import argparse
import time
from pathlib import Path
from typing import List, Dict
import re, os

import faiss
import h5py
import numpy as np
import torch
from . import logger, matchers

# 确保项目根目录在 PYTHONPATH 中
import sys
from pathlib import Path as PathLib

sys.path.append(str(PathLib(__file__).resolve().parent))

from hloc.my_extract_features_and_retrival import confs, init_model, extract_single_image
from hloc.my_pairs_from_retrival import load_database_descriptors, build_faiss_index, retrieve_topk
from hloc.match_features import dynamic_load
from hloc import my_match_features
from my_pkg.tools import sort_key, pixel_to_geo_coordinates

def list_h5_names(path: Path):
    with h5py.File(str(path), "r") as fd:
        return list(fd.keys())

def load_lightglue_model(conf: Dict, device: torch.device):
    """
    动态加载 LightGlue 模型。
    """
    from hloc.matchers import lightglue  # 确保 LightGlue 模型在 matchers 模块中
    Model = dynamic_load(lightglue, conf["model"]["name"])
    model = Model(conf["model"]).eval().to(device)
    return model

def load_lightglue_model(conf: Dict, device: torch.device):
    """
    动态加载 LightGlue 模型。
    """
    from hloc.matchers import lightglue  # 确保 LightGlue 模型在 matchers 模块中
    Model = dynamic_load(lightglue, conf["model"]["name"])
    model = Model(conf["model"]).eval().to(device)
    return model


def perform_feature_matching(lightglue_model, device: torch.device,
                            query_desc, db_desc):
    """
    使用 LightGlue 模型进行特征点匹配。
    """

    # 假设 SuperPoint 描述子包含关键点位置和描述子
    # query_desc 和 db_desc 应该包含 'keypoints' 和 'descriptors'

    # 创建输入数据
    data = {
        "keypoints0": torch.from_numpy(query_desc['keypoints']).float().to(device),
        "descriptors0": torch.from_numpy(query_desc['descriptors']).float().to(device),
        "keypoints1": torch.from_numpy(db_desc['keypoints']).float().to(device),
        "descriptors1": torch.from_numpy(db_desc['descriptors']).float().to(device),
    }
    print("data:", data)


    # 模型推理
    with torch.no_grad():
        pred = lightglue_model(data)

    return pred

# 从数据库中检索 top-k
def run_incremental_retrieve(
        conf: str,
        match_conf: Dict,
        db_feature_path: Path,
        query_image_dir: Path,
        query_feature_path: Path,
        sp_feature_path: Path,
        output_pairs: Path,
        topk: int = 5,
        as_half: bool = True,
        overwrite: bool = False
):
    loc_path = Path("/home/lty/outputs/scene_match_0103_seu_2/scene_loc.txt")
    angle = 0
    # 验证配置是否存在
    if conf not in confs:
        raise ValueError(f"Configuration '{conf}' not found. Available configurations: {list(confs.keys())}")

    # 加载配置
    config = confs[conf]

    # 初始化模型
    model, device = init_model(config)
    print(f"Initialized model '{conf}' on {device}.")

    # 加载 LightGlue 模型
    Model = dynamic_load(matchers, match_conf["model"]["name"])
    lg_model = Model(match_conf["model"]).eval().to(device)
    print("Loaded LightGlue model.")
    # 加载数据库特征
    # print(f"Loading database features from {db_feature_path}.")
    db_desc, db_names = load_database_descriptors([db_feature_path], key="global_descriptor")
    # print(f"Loaded {db_desc.shape[0]} database descriptors.")
    db_desc = db_desc.astype(np.float32)
    faiss.normalize_L2(db_desc)  # 归一化

    # 构建或加载 FAISS 索引
    print("Building FAISS index.")
    index = build_faiss_index(db_desc, use_gpu=True)
    print(f"FAISS index built with {index.ntotal} database descriptors.")

    query_dir_name = query_image_dir.name

    # 打开输出文件
    with open(output_pairs, "w") as output_file,open(loc_path, 'w') as loc_file:
        # 处理每张查询图像
        query_images = sorted(query_image_dir.glob("*.[jp][pn]g"))  # 简单的图像匹配
        t1 = time.time()
        n =0
        for query_image_path in query_images:
            print(f"Processing query image: {query_image_path.name}")
            sp_query_name = f"{query_dir_name}/{query_image_path.name}"

            # 提取查询图像特征
            query_desc = extract_single_image(
                model=model,
                device=device,
                conf=config,
                image_path=query_image_path,
                feature_path=query_feature_path,
                as_half=as_half,
                overwrite=overwrite,
            )
            if query_desc is None:
                print(f"Feature extraction failed for {query_image_path.name}.")
            # 读取查询描述子
                with h5py.File(str(query_feature_path), "r") as fd:
                    query_name = query_image_path.stem
                    if query_name not in fd:
                        print(f"Feature for {query_name} not found after extraction.")
                        continue
                    if "global_descriptor" not in fd[query_name]:
                        print(f"No global_descriptor found for {query_name}.")
                        continue
                    query_desc = fd[query_name]["global_descriptor"][:].astype(np.float32)
                    # print(f"Query descriptor shape: {query_desc.shape}")
                    # print(f"Query descriptor: {query_desc}")
            query_desc = query_desc[:].astype(np.float32)
            faiss.normalize_L2(query_desc.reshape(1, -1))

            # 检索 top-k
            first_idx = None
            D, I = index.search(query_desc.reshape(1, -1), topk)
            for rank, (idx, score) in enumerate(zip(I[0], D[0])):
                matched_name = db_names[idx]
                output_file.write(f"{query_name} {matched_name} {score}\n")
                if rank == 0:
                    first_idx = idx
                # print(f"  Match {rank + 1}: {matched_name} with score {score}")
            print(f"  Best match: {db_names[first_idx]} with score {D[0][0]}")

            # print(f"Processed query image: {sp_query_name}")
            img_pairs = [(sp_query_name, db_names[first_idx])]
            t3 = time.time()
            center_tif = my_match_features.main(
                match_conf,
                pairs=img_pairs,
                features=sp_feature_path,
                model=lg_model,
                matches = Path("/home/lty/outputs/scene_match_0103_seu_2/SP+LG_matches.h5"),
            )
            t4 = time.time()
            print(f"wurenji center_tif: {center_tif}")
            pixel_x, pixel_y = center_tif
            tif_name = os.path.basename(db_names[first_idx])
            match = re.match(r"(\d+)_(\d+)_(\d+).tif", tif_name)
            if match:
                start_x = match.group(2)
                start_y = match.group(3)
                x_in_map = int(start_x) + pixel_x
                y_in_map = int(start_y) + pixel_y
                print(f"无人机图像中心点在地图上的位置：{x_in_map},{y_in_map}")
            print(f"Matching completed in {t4 - t3:.3f} s.")
            geotransform = [668601.89603705, 0.03459999999999788, 0.0, 3548451.1491134795, 0.0, -0.03459999999998963]
            lon, lat, x_geo, y_geo = pixel_to_geo_coordinates(x_in_map, y_in_map, geotransform)
            print(f"无人机图像中心点的经纬度：{lat}, {lon}")
            if n == 0:
                x_origin, y_origin = x_geo, y_geo
            loc_file.write(
                f"{sp_query_name} {lon:.8f} {lat:.8f} {x_in_map:.8f} {y_in_map:.8f} {x_geo:.8f} {y_geo:.8f} {x_geo - x_origin:.10f} {y_origin - y_geo:.10f} {angle:.8f}\n")

            n+=1
        t2 = time.time()
        print(f"Retrieval completed in {t2 - t1:.3f} s.")
    print(f"Retrieved pairs saved to {output_pairs}.")


def main():
    parser = argparse.ArgumentParser(description="Incremental Feature Extraction and Retrieval for UAV Images.")
    parser.add_argument("--conf", type=str, default="netvlad", choices=list(confs.keys()),
                        help="Feature extraction configuration.")
    parser.add_argument(
        "--match_conf", type=str, default="superglue", choices=list(confs.keys())
    )
    parser.add_argument("--db_feature_path", type=Path, required=True,
                        help="Path to pre-extracted database features (.h5).")
    parser.add_argument("--sp_feature_path", type=Path, required=True,
                        help="Path to pre-extracted superpoint features (.h5).")
    parser.add_argument("--query_image_dir", type=Path, required=True, help="Directory containing UAV query images.")
    parser.add_argument("--query_feature_path", type=Path, required=True,
                        help="Path to save extracted query features (.h5).")
    parser.add_argument("--output_pairs", type=Path, required=True, help="Path to save retrieved image pairs.")
    parser.add_argument("--topk", type=int, default=5, help="Number of top matches to retrieve.")
    parser.add_argument("--as_half", action="store_true", help="Store features as half precision.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing features.")
    args = parser.parse_args()

    run_incremental_retrieve(
        conf=args.conf,
        match_conf=args.match_conf,
        db_feature_path=args.db_feature_path,
        sp_feature_path=args.sp_feature_path,
        query_image_dir=args.query_image_dir,
        query_feature_path=args.query_feature_path,
        output_pairs=args.output_pairs,
        topk=args.topk,
        as_half=args.as_half,
        overwrite=args.overwrite
    )

if __name__ == "__main__":
    main()
