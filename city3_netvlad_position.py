import cv2
import numpy as np
import re
from pathlib import Path
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import h5py

from hloc import extract_features, match_features, pairs_from_retrieval,my_extract_features_and_retrival
from hloc.utils.io import get_matches, get_keypoints
from my_pkg.tools import sort_key, pixel_to_geo_coordinates, read_pairs, extract_rotation_angle
import time
from hloc.my_incremental_extract_retrive import run_incremental_retrieve

output_dir = Path("/home/lty/outputs/RealUAV/city3/netvlad")
output_dir.mkdir(exist_ok=True, parents= True)
output_dir_db = output_dir / "db"
output_dir_db.mkdir(exist_ok=True, parents= True)
output_dir_query = output_dir / "query"
query_global_descriptors = output_dir_query / "query_global_descriptors.h5"
superpoint_features = Path("/home/lty/outputs/RealUAV/city3/features.h5")
output_dir_query.mkdir(exist_ok=True, parents= True)
netvlad_pairs = output_dir / "pairs-query-netvlad20.txt"
image_dir = Path("/home/lty/datasets/RealUAV/city3/")
query_image_dir = Path("/home/lty/datasets/RealUAV/city3/uav")
img_list = Path("/home/lty/outputs/RealUAV/city3/img_list.txt")
db_list = Path("/home/lty/outputs/RealUAV/city3/tif_list.txt")
query_list = Path("/home/lty/outputs/RealUAV/city3/uav_list.txt")

retrieval_conf = extract_features.confs["netvlad"]
t1 = time.time()
db_global_descriptors = extract_features.main(retrieval_conf, image_dir, output_dir_db, image_list=db_list)
t2 = time.time()
print(f"Extracting global descriptors for database images costs {t2 - t1:.3f} s.")

run_incremental_retrieve(
    "netvlad",
    db_feature_path=db_global_descriptors,
    query_image_dir=query_image_dir,
    query_feature_path=query_global_descriptors,
    sp_feature_path=superpoint_features,
    output_pairs=netvlad_pairs,
    match_conf=match_features.confs["superpoint+lightglue"],
    topk=5,
    as_half=True,
    overwrite=False
)