import os
os.environ['PROJ_LIB'] = '/home/lty/anaconda3/envs/hloc/share/proj'
from osgeo import osr
from my_pkg.tools import parse_keyframe_file
from math import sqrt

def ComputeAndSaveError(gt_file, loc_file, KeyFrameId_file, error_file):

    keyframe_mapping = parse_keyframe_file(KeyFrameId_file)

    source_srs = osr.SpatialReference()
    source_srs.ImportFromEPSG(4326)
    target_srs = osr.SpatialReference()
    target_srs.ImportFromEPSG(3857)
    coord_transform = osr.CoordinateTransformation(source_srs, target_srs)

    gt_data = []
    with open(gt_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # 假设格式为: 118.7865, 32.0591
            parts = line.split(",")
            if len(parts) == 2:
                lon_str, lat_str = parts
                lon = float(lon_str.strip())
                lat = float(lat_str.strip())
                x, y, _ = coord_transform.TransformPoint(lat, lon)
                gt_data.append((x, y))
    loc_data = []
    with open(loc_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            parts = line.strip().split()
            if len(parts) < 10:
                continue
            x_geo = parts[5]
            y_geo = parts[6]
            x_geo = float(x_geo)
            y_geo = float(y_geo)
            loc_data.append((x_geo, y_geo))
    results =[]
    # 遍历 keyframe_mapping，计算每个关键帧的误差
    # keyframe_mapping[keyframe_id] = frame_id
    print(f"keyframe_mapping: {keyframe_mapping}")
    n = 0
    ex_all = 0
    ey_all = 0
    dist_all = 0
    d_all = 0
    d = 0
    last_x_gt = 0
    last_y_gt = 0
    for frame_id in keyframe_mapping.values():
        # 如果 keyframe_id 超出 slam_data 的长度，说明对应不到位姿
        # print(f"frame_id: {frame_id}")
        # 取 SLAM 估计值
        x_slam, y_slam = loc_data[frame_id]
        n+=1

        # 取真值
        # 如果 frame_id 超出 gt_data 的长度，需要根据实际情况做异常处理
        if frame_id >= len(gt_data):
            continue
        x_gt, y_gt = gt_data[frame_id]
        if n == 1:
            last_x_gt = x_gt
            last_y_gt = y_gt

        # 计算误差
        ex = (x_slam - x_gt)
        ey = (y_slam - y_gt)
        ex_abs = abs(x_slam - x_gt)
        ey_abs = abs(y_slam - y_gt)
        dist = sqrt(ex ** 2 + ey ** 2)

        d = sqrt((x_gt - last_x_gt) ** 2 + (y_gt - last_y_gt) ** 2)
        d_all += d
        last_x_gt = x_gt
        last_y_gt = y_gt

        results.append((n, frame_id, ex_abs, ey_abs, dist, d_all))

        ex_all += ex_abs
        ey_all += ey_abs
        dist_all += dist
        # 将误差写入文件（文件不存在就创建）
    with open(error_file, "w", encoding="utf-8") as f:
        # 标题行（可选）
        # f.write("KeyFrameID, FrameID, ErrorX, ErrorY, Distance\n")
        for (kf_id, frm_id, ex_abs, ey_abs, dist, d_all) in results:
            f.write(f"{frm_id}, {ex_abs:.4f}, {ey_abs:.4f}, {dist:.4f}, {d_all:.4f}\n")

    print(f"定位误差已经写入到 {error_file} 中。")
    ex_everage = ex_all / len(results)
    ey_everage = ey_all / len(results)
    dist_everage = dist_all / len(results)
    print("data length: ", len(results))
    print(f"ex_everage: {ex_everage}")
    print(f"ey_everage: {ey_everage}")
    print(f"dist_everage: {dist_everage}")

    print()


if __name__ == '__main__':
    gt_file = "/home/lty/datasets/RealUAV/city1/gt.txt"
    KeyFrameId_file = "/home/lty/outputs/RealUAV/city1/KeyFrameId.txt"
    error_file = "/home/lty/outputs/RealUAV/city1/error_pure_scene.txt"
    loc_file = "/home/lty/outputs/RealUAV/city1/loc.txt"



    ComputeAndSaveError(gt_file, loc_file, KeyFrameId_file, error_file)
