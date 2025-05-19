from pathlib import Path
import re

from numexpr.necompiler import double
from osgeo import osr
import cv2
import numpy as np
def sort_key(filepath):
    """
    提取文件名中的第一个数字作为排序关键字。
    如果文件名中没有数字，则返回 0。
    """
    match = re.search(r'(\d+)', Path(filepath).stem)
    return int(match.group(1)) if match else 0

def read_pairs(pairs_file):
    """
    读取 pairs.txt 文件，解析每一行无人机图片和 TIF 影像的路径。
    """
    pairs = []
    with open(pairs_file, 'r') as f:
        for line in f:
            # 分割每行路径，假设格式为 "seu_uav/DJI_0001.JPG seu_tif/37_12000_6000.tif"
            pair = line.strip().split()
            if len(pair) == 2:
                pairs.append(pair)
    return pairs

def pixel_to_geo_coordinates(x, y, geotransform, source_epsg=3857, target_epsg=4326):
    """
    将像素坐标转换为经纬度坐标。

    参数:
    - x, y: 输入的像素坐标 (x, y)。
    - geotransform: 地理变换参数，包含 (x_origin, x_pixel_size, x_rotation, y_origin, y_rotation, y_pixel_size)。
    - source_epsg: 源坐标系的 EPSG 编号 (默认 32650)。
    - target_epsg: 目标坐标系的 EPSG 编号 (默认 4326)。

    返回:
    - lat, lon: 转换后的经纬度坐标。
    """
    if not geotransform:
        raise ValueError("地理变换参数 geotransform 不能为空。")

    # 解包地理变换参数
    x_origin, x_pixel_size, x_rotation, y_origin, y_rotation, y_pixel_size = geotransform

    # 计算地理坐标（EPSG:source_epsg）
    x_geo = x_origin + x_pixel_size * x + x_rotation * y
    y_geo = y_origin + y_rotation * x + y_pixel_size * y

    # 创建源坐标系和目标坐标系
    source_srs = osr.SpatialReference()
    source_srs.ImportFromEPSG(source_epsg)

    target_srs = osr.SpatialReference()
    target_srs.ImportFromEPSG(target_epsg)

    # 创建坐标转换对象
    coord_transform = osr.CoordinateTransformation(source_srs, target_srs)

    # 转换为经纬度坐标（EPSG:target_epsg）
    z = 0
    lat, lon, _ = coord_transform.TransformPoint(x_geo, y_geo, z)


    return lon, lat, x_geo, y_geo

def plot_traj_tif(map_image_path, loc_file_path, output_image_path, scale_factor):
    """
    在缩放后的地图图像上绘制轨迹。

    参数:
    - map_image_path: 地图图像的路径（.tif 或其他支持的图像格式）。
    - loc_file_path: 包含轨迹点 (x_in_map, y_in_map) 的 loc.txt 文件路径。
    - output_image_path: 输出包含轨迹的图像路径。
    - scale_factor: 地图缩放比例（例如 0.2 表示地图缩放为原来的五分之一）。
    """
    # 读取地图图像
    map_image = cv2.imread(map_image_path, cv2.IMREAD_COLOR)
    if map_image is None:
        raise FileNotFoundError(f"无法加载地图图像: {map_image_path}")

    # 打开 loc.txt 并读取点
    points = []
    with open(loc_file_path, 'r') as loc_file:
        for line in loc_file:
            parts = line.strip().split()
            if len(parts) < 4:
                continue
            x_in_map = float(parts[3]) * scale_factor  # 调整横坐标
            y_in_map = float(parts[4]) * scale_factor  # 调整纵坐标
            print(f"{parts[0]}: {x_in_map}, {y_in_map}")
            points.append((x_in_map, y_in_map))

    # 将点转换为整数坐标（像素坐标）
    points = [(int(x), int(y)) for x, y in points]

    # 在地图图像上绘制轨迹
    for i in range(len(points)):
        # 绘制当前点
        cv2.circle(map_image, points[i], radius=3, color=(0, 0, 255), thickness=-1)  # 红色点
        # 如果不是第一个点，绘制线段
        if i > 0 :
            cv2.line(map_image, points[i - 1], points[i], color=(255, 255, 0), thickness=6)  # 蓝色线

    # 保存绘制结果
    cv2.imwrite(output_image_path, map_image)
    print(f"轨迹图像已保存到: {output_image_path}")

# 解析 keyframeid.txt 文件，获取关键帧和对应图像的映射关系
def parse_keyframe_file(file_path):
    keyframe_mapping = {}
    with open(file_path, "r") as f:
        for line in f:
            if line.strip():  # 跳过空行
                parts = line.strip().split(",")
                keyframe_id = int(parts[0].split(":")[1].strip())
                frame_id = int(parts[1].split(":")[1].strip())
                keyframe_mapping[keyframe_id] = frame_id
    return keyframe_mapping

# 在地图图像上绘制轨迹，只绘制关键帧对应的点
def draw_keyframe_trajectory(map_image, points, keyframe_mapping):
    keyframe_points = [points[frame_id] for frame_id in keyframe_mapping.values() if frame_id < len(points)]

    # 绘制关键帧点和连线
    for i in range(len(keyframe_points)):
        # 绘制当前关键帧点
        cv2.circle(map_image, keyframe_points[i], radius=1, color=(0, 255, 0), thickness=6)  # 绿色点
        # 如果不是第一个点，绘制关键帧之间的连线
        if i > 0:
            cv2.line(map_image, keyframe_points[i - 1], keyframe_points[i], color=(255, 0, 0), thickness=6)  # 蓝色线

    return map_image

def draw_fusion_keyframe_traj(map_image, points):
    for i in range(len(points)):
        # 绘制当前关键帧点
        cv2.circle(map_image, points[i], radius=1, color=(255, 255, 0), thickness=6)
        # 如果不是第一个点，绘制关键帧之间的连线
        if i > 0:
            cv2.line(map_image, points[i - 1], points[i], color=(0, 0, 255), thickness=6)
    return map_image

def draw_slam_keyframe_traj(map_image, points):
    for i in range(len(points)):
        # 绘制当前关键帧点
        cv2.circle(map_image, points[i], radius=1, color=(255, 255, 0), thickness=6)
        # 如果不是第一个点，绘制关键帧之间的连线
        if i > 0:
            cv2.line(map_image, points[i - 1], points[i], color=(0, 255, 255), thickness=6)
    return map_image


def extract_rotation_angle(H):
    # 标准化 H 矩阵
    H_normalized = H / H[2, 2]

    # 提取旋转矩阵部分
    R = H_normalized[0:2, 0:2]

    # 使用 SVD 进行正交化
    U, S, Vt = np.linalg.svd(R)
    R_ortho = U @ Vt

    # 确保 R_ortho 是一个有效的旋转矩阵
    if np.linalg.det(R_ortho) < 0:
        R_ortho = U @ np.diag([1, -1]) @ Vt

    # 计算旋转角度
    theta_rad = np.arctan2(R_ortho[1, 0], R_ortho[0, 0])
    theta_deg = np.degrees(theta_rad)

    return theta_deg


def rotate_point_z(point, angle_deg):
    """
    绕 Z 轴旋转一个三维点。

    参数:
    - point (list or tuple or np.ndarray): 要旋转的点，格式为 [x, y, z]
    - angle_deg (float): 旋转角度，单位为度

    返回:
    - np.ndarray: 旋转后的点坐标
    """
    # 将角度转换为弧度
    angle_rad = np.deg2rad(angle_deg)

    # 定义绕 Z 轴的旋转矩阵
    R_z = np.array([
        [np.cos(angle_rad), -np.sin(angle_rad), 0],
        [np.sin(angle_rad), np.cos(angle_rad), 0],
        [0, 0, 1]
    ])

    # 确保输入点是 NumPy 数组
    point = np.array(point)

    # 检查点的维度
    if point.shape != (3,):
        raise ValueError("输入的点必须是三维的，格式为 [x, y, z]")

    # 应用旋转矩阵
    rotated_point = R_z @ point

    return rotated_point, R_z