# hloc/pairs_from_retrival.py

import argparse
import collections.abc as collections
from pathlib import Path
from typing import Optional, List, Dict, Union

import h5py
import numpy as np
import torch
import faiss

from . import logger
from .utils.io import list_h5_names
from .utils.parsers import parse_image_lists
from .utils.read_write_model import read_images_binary

def parse_names(prefix, names, names_all):
    if prefix is not None:
        if not isinstance(prefix, str):
            prefix = tuple(prefix)
        names = [n for n in names_all if n.startswith(prefix)]
        if len(names) == 0:
            raise ValueError(f"Could not find any image with the prefix `{prefix}`.")
    elif names is not None:
        if isinstance(names, (str, Path)):
            names = parse_image_lists(names)
        elif isinstance(names, collections.Iterable):
            names = list(names)
        else:
            raise ValueError(
                f"Unknown type of image list: {names}."
                "Provide either a list or a path to a list file."
            )
    else:
        names = names_all
    return names

def get_descriptors(names, path, name2idx=None, key="global_descriptor"):
    if name2idx is None:
        with h5py.File(str(path), "r", libver="latest") as fd:
            desc = [fd[n][key].__array__() for n in names]
    else:
        desc = []
        for n in names:
            with h5py.File(str(path[name2idx[n]]), "r", libver="latest") as fd:
                desc.append(fd[n][key].__array__())
    return torch.from_numpy(np.stack(desc, 0)).float()

def pairs_from_score_matrix(
    scores: torch.Tensor,
    invalid: np.array,
    num_select: int,
    min_score: Optional[float] = None,
):
    assert scores.shape == invalid.shape
    if isinstance(scores, np.ndarray):
        scores = torch.from_numpy(scores)
    invalid = torch.from_numpy(invalid).to(scores.device)
    if min_score is not None:
        invalid |= scores < min_score
    scores.masked_fill_(invalid, float("-inf"))

    topk = torch.topk(scores, num_select, dim=1)
    indices = topk.indices.cpu().numpy()
    valid = topk.values.isfinite().cpu().numpy()

    pairs = []
    for i, j in zip(*np.where(valid)):
        pairs.append((i, indices[i, j]))
    return pairs

def load_database_descriptors(db_descriptors: List[Path], key: str = "global_descriptor"):
    """
    加载数据库的全局描述子并返回一个 NumPy 数组。
    """
    descriptors = []
    db_names = []
    for db_path in db_descriptors:
        with h5py.File(str(db_path), "r") as fd:
            for name in list_h5_names(db_path):
                if key in fd[name]:
                    desc = fd[name][key][:]
                    descriptors.append(desc)
                    db_names.append(name)
    descriptors = np.stack(descriptors, axis=0).astype(np.float32)
    return descriptors, db_names

def build_faiss_index(descriptors: np.ndarray, use_gpu: bool = True):
    """
    使用 FAISS 构建索引。如果 use_gpu=True，则将索引迁移到GPU。
    """
    dimension = descriptors.shape[1]
    index_cpu = faiss.IndexFlatIP(dimension)  # 使用内积作为相似度度量（等效于余弦相似度）
    faiss.normalize_L2(descriptors)  # 归一化
    index_cpu.add(descriptors)

    if use_gpu and faiss.get_num_gpus() > 0:

        res = faiss.StandardGpuResources()
        index_gpu = faiss.index_cpu_to_gpu(res, 0, index_cpu)
        logger.info("FAISS index moved to GPU.")
        return index_gpu
    else:
        logger.warning("FAISS is not using GPU. Using CPU instead.")
        return index_cpu

def retrieve_topk(query_descriptor: np.ndarray, index: faiss.Index, db_names: List[str], topk: int = 5):
    """
    使用 FAISS 检索 top-k 结果。
    """
    query = query_descriptor.astype(np.float32).reshape(1, -1)
    faiss.normalize_L2(query)
    D, I = index.search(query, topk)
    results = [(db_names[idx], float(D[0][i])) for i, idx in enumerate(I[0])]
    return results

def main(
    descriptors,
    output,
    num_matched,
    query_prefix=None,
    query_list=None,
    db_prefix=None,
    db_list=None,
    db_model=None,
    db_descriptors=None,
):
    logger.info("Extracting image pairs from a retrieval database.")

    # 处理多个数据库描述子文件
    if db_descriptors is None:
        db_descriptors = descriptors
    if isinstance(db_descriptors, (Path, str)):
        db_descriptors = [db_descriptors]
    name2db = {n: i for i, p in enumerate(db_descriptors) for n in list_h5_names(p)}
    db_names_h5 = list(name2db.keys())
    query_names_h5 = list_h5_names(descriptors)

    if db_model:
        images = read_images_binary(db_model / "images.bin")
        db_names = [i.name for i in images.values()]
    else:
        db_names = parse_names(db_prefix, db_list, db_names_h5)
    if len(db_names) == 0:
        raise ValueError("Could not find any database image.")
    query_names = parse_names(query_prefix, query_list, query_names_h5)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    db_desc = get_descriptors(db_names, db_descriptors)
    query_desc = get_descriptors(query_names, descriptors)
    sim = torch.einsum("id,jd->ij", query_desc.to(device), db_desc.to(device))

    # 避免自匹配
    self_matches = np.array(query_names)[:, None] == np.array(db_names)[None]
    pairs = pairs_from_score_matrix(sim, self_matches, num_matched, min_score=0)
    pairs = [(query_names[i], db_names[j]) for i, j in pairs]

    logger.info(f"Found {len(pairs)} pairs.")
    with open(output, "w") as f:
        f.write("\n".join(" ".join([i, j]) for i, j in pairs))
