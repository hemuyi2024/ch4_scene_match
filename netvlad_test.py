import cv2
import numpy as np
import re
from pathlib import Path
import os
import h5py
from hloc import extract_features, match_features, pairs_from_retrieval,my_extract_features_and_retrival
from hloc.utils.io import get_matches, get_keypoints
from my_pkg.tools import sort_key, pixel_to_geo_coordinates, read_pairs, extract_rotation_angle
import time

output_dir = Path("/home/lty/outputs/scene_match_12-26_seu/netvlad")
output_dir.mkdir(exist_ok=True, parents= True)
output_dir_db = output_dir / "db"
output_dir_db.mkdir(exist_ok=True, parents= True)
output_dir_query = output_dir / "query"
output_dir_query.mkdir(exist_ok=True, parents= True)
netvlad_pairs = output_dir / "pairs-query-netvlad20.txt"
image_dir = Path("/home/lty/datasets_my/DJI/m300/")
img_list = Path("/home/lty/outputs/scene_match_12-26_seu/img_list.txt")
db_list = Path("/home/lty/outputs/scene_match_12-26_seu/tif_list.txt")
query_list = Path("/home/lty/outputs/scene_match_12-26_seu/uav_list.txt")

retrieval_conf = extract_features.confs["netvlad"]
t1 = time.time()
db_global_descriptors = extract_features.main(retrieval_conf, image_dir, output_dir_db, image_list=db_list)
t2 = time.time()
print(f"Extracting global descriptors for database images costs {t2 - t1:.3f} s.")

my_extract_features_and_retrival.main_my(retrieval_conf, image_dir, output_dir_query, image_list=query_list)
t3 = time.time()
print(f"Extracting global descriptors for query images costs {t3 - t2:.3f} s.")