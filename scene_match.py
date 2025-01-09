import cv2
import numpy as np
import matplotlib.pyplot as plt
import re
from pathlib import Path
import os
# os.environ['PROJ_LIB'] = '/home/lty/anaconda3/envs/hloc/share/proj'

from osgeo import gdal, osr
from geopy.distance import geodesic

from hloc import extract_features, match_features
from hloc.utils.io import get_matches, get_keypoints
from hloc.visualization import plot_images, plot_keypoints, plot_matches, read_image, add_text

image_dir = Path("/home/lty/datasets_my/DJI/phantom4/11-12-playground/11-12-1080p/")
img_1  = "seu_uav/DJI_0218.JPG"
img_2 = "seu_tif/37_12000_6000.tif"
img_list = [img_1, img_2]
output_dir = Path("/home/lty/outputs/hloc_scene_match")
output_dir.mkdir(exist_ok=True, parents=True)
pairs_path = output_dir / "pairs.txt"

if __name__ == '__main__':
    print(f"无人机图片文件夹路径：{image_dir}")