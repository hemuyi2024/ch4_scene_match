import os
os.environ['PROJ_LIB'] = '/home/lty/anaconda3/envs/hloc/share/proj'
from osgeo import osr
import numpy as np


def convert_gt_to_loc(gt_path, geotransform_path, save_path, prefix="uav/", image_ext=".png"):
    # Step 1: 读取 geotransform 参数
    geotransform = []
    with open(geotransform_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                geotransform.append(float(line))

    if len(geotransform) != 6:
        raise ValueError("geotransform.txt 格式不正确，必须包含6个浮点数")

    x_origin_gt, x_res, x_rot, y_origin_gt, y_rot, y_res = geotransform

    # Step 2: 设置坐标转换（WGS84 → EPSG:3857）
    source_srs = osr.SpatialReference()
    source_srs.ImportFromEPSG(4326)  # WGS84
    target_srs = osr.SpatialReference()
    target_srs.ImportFromEPSG(32650)  # 投影坐标
    coord_transform = osr.CoordinateTransformation(source_srs, target_srs)

    # Step 3: 读取 GT 文件并转换
    with open(gt_path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    output_lines = []
    for i, line in enumerate(lines):
        lon_str, lat_str = map(str.strip, line.split(","))
        lon = float(lon_str)
        lat = float(lat_str)
        x_geo, y_geo, _ = coord_transform.TransformPoint(lat, lon)

        if i == 0:
            x_origin_truth, y_origin_truth = x_geo, y_geo
            # x_origin, y_origin = 12123905.77494, 4061590.61553926

        dx = x_geo - x_origin_truth
        dy = y_origin_truth - y_geo  # 注意保持与你的格式一致（南方为正）
        # dx2 = x_geo-x_origin
        # dy2 = y_origin-y_geo

        # dx = (dx1*5+dx2*4)/9
        # dy = (dy1*5+dy2*4)/9
        # if i == 0:
        #     dx = 0
        #     dy = 0
        #
        # if i<=10:
        #     dx = x_geo - x_origin_truth
        #     dy = y_origin_truth - y_geo
        x_in_map = 0
        y_in_map = 0
        angle = 0

        image_name = f"{prefix}{i:04d}{image_ext}"
        output_lines.append(
            f"{image_name} {lon:.8f} {lat:.8f} {x_in_map:.8f} {y_in_map:.8f} {x_geo:.8f} {y_geo:.8f} {dx:.10f} {dy:.10f} {angle:.8f}")

    # Step 4: 写入 loc.txt
    with open(save_path, 'w') as f:
        for line in output_lines:
            f.write(line + "\n")

    print(f"转换完成，共 {len(output_lines)} 条，已保存至 {save_path}")


# 示例调用
if __name__ == "__main__":
    gt_path = "/home/lty/outputs/scene_match_seu_0110_6/gt.txt"
    geotransform_path = "/home/lty/scripts/seu_geotransform_m300.txt"
    save_path = "/home/lty/outputs/scene_match_seu_0110_6/loc_from_gt.txt"

    convert_gt_to_loc(gt_path, geotransform_path, save_path)
