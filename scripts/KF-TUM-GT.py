import re
import math
from osgeo import osr
import numpy as np
from my_pkg.tools import parse_keyframe_file

def replace_keyframe_xyz(keyframe_id_path, keyframe_traj_path, gt_traj_path, output_path):
    """
    根据 keyframeid.txt 中的 Frame ID（第二列），找到 tum_gt.txt 中第 (Frame ID + 1) 行的 groundtruth xyz，
    并替换 keyframetraj.txt 中对应行的 xyz，保持时间戳和四元数不变。
    """
    # 读取 groundtruth 文件并按行存储
    gt_data = []
    with open(gt_traj_path, 'r') as f:
        for line in f:
            if line.strip():
                gt_data.append(line.strip().split())

    # 加载 keyframe traj 原始数据
    with open(keyframe_traj_path, 'r') as f:
        keyframe_lines = [line.strip() for line in f if line.strip()]

    # 遍历 keyframe_id，找到对应的 Frame ID 后，拿 groundtruth 替换 xyz
    keyframe_mapping = parse_keyframe_file(keyframe_id_path)
    replaced_lines = []
    id = 0
    for frame_id in keyframe_mapping.values():
        # 如果 keyframe_id 超出 slam_data 的长度，说明对应不到位姿
        if frame_id >= len(gt_data):
            print(f"⚠️ Frame ID {frame_id} 超出 groundtruth 数据长度，忽略该帧")
            continue

        # 获取 keyframe 原时间戳和四元数
        kf_parts = keyframe_lines[id].split()
        id += 1
        timestamp = kf_parts[0]
        quat = kf_parts[4:]

        # 获取第 frame_id + 1 行的 groundtruth xyz
        gt_xyz = gt_data[frame_id + 1][1:4]

        # 组装新的行
        replaced_line = f"{timestamp} {' '.join(gt_xyz)} {' '.join(quat)}"
        replaced_lines.append(replaced_line)

    # 写入文件
    with open(output_path, 'w') as f:
        f.write('\n'.join(replaced_lines))

    print(f"✅ 替换完成，生成 {output_path}，共 {len(replaced_lines)} 条数据")


if __name__ == "__main__":
    replace_keyframe_xyz(
        keyframe_id_path='/home/lty/code/ORB_SLAM3_detailed_comments/KeyFrameId.txt',
        keyframe_traj_path='/home/lty/code/ORB_SLAM3_detailed_comments/traj/KeyFrameTrajectoryGeo.txt',
        gt_traj_path='/home/lty/datasets_my/DJI/m300/DJI_0110_6_W_tum_cut.txt',
        output_path='keyframe_gt.txt'
    )
