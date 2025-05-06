import re
import math
from osgeo import osr
import numpy as np

def euler_to_quaternion(yaw, pitch, roll):
    """欧拉角（度）转四元数，ZYX顺序"""
    yaw_rad = math.radians(yaw)
    pitch_rad = math.radians(pitch)
    roll_rad = math.radians(roll)

    cy = math.cos(yaw_rad * 0.5)
    sy = math.sin(yaw_rad * 0.5)
    cp = math.cos(pitch_rad * 0.5)
    sp = math.sin(pitch_rad * 0.5)
    cr = math.cos(roll_rad * 0.5)
    sr = math.sin(roll_rad * 0.5)

    qw = cr * cp * cy + sr * sp * sy
    qx = sr * cp * cy - cr * sp * sy
    qy = cr * sp * cy + sr * cp * sy
    qz = cr * cp * sy - sr * sp * cy
    return np.array([qx, qy, qz, qw])

def quaternion_inverse(q):
    """四元数求逆"""
    q_conj = np.array([-q[0], -q[1], -q[2], q[3]])
    return q_conj / np.dot(q, q)

def quaternion_multiply(q1, q2):
    """四元数相乘"""
    x1, y1, z1, w1 = q1
    x2, y2, z2, w2 = q2
    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2
    z = w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2
    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
    return np.array([x, y, z, w])

def extract_tum_with_quaternion(srt_file_path, output_file_path):
    """
    提取经纬度、高度和相机姿态信息（转四元数），保存为TUM格式
    """
    global first_x, first_y, first_z
    try:
        with open(srt_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"文件未找到: {srt_file_path}")
        return
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return

    # 匹配每个字幕块（从FrameCnt开始）
    block_pattern = re.compile(
        r'FrameCnt:.*?\[latitude:\s*([-+]?\d*\.\d+)\]\s*\[longitude:\s*([-+]?\d*\.\d+)\]'
        r'\s*\[rel_alt:\s*([-+]?\d*\.\d+).*?\]'
        r'.*?\[gb_yaw:\s*([-+]?\d*\.\d+)\s*gb_pitch:\s*([-+]?\d*\.\d+)\s*gb_roll:\s*([-+]?\d*\.\d+)\]',
        re.DOTALL
    )

    matches = block_pattern.findall(content)

    if not matches:
        print("未找到任何匹配的经纬度和姿态信息。")
        return

    # 30FPS时间戳递增
    timestamp = 0.0
    time_increment = 155.382 / 2173.0  # 30fps

    tum_data = []
    source_srs = osr.SpatialReference()
    source_srs.ImportFromEPSG(4326)
    target_srs = osr.SpatialReference()
    target_srs.ImportFromEPSG(32650)
    coord_transform = osr.CoordinateTransformation(source_srs, target_srs)

    first = matches[0]
    base_q = euler_to_quaternion(float(first[3]), float(first[4]), float(first[5]))
    base_q_inv = quaternion_inverse(base_q)

    num = 0
    for lat, lon, rel_alt, gb_yaw, gb_pitch, gb_roll in matches:
        # 位置直接用经纬度和相对高度
        tx, ty, tz = float(lon), float(lat), float(rel_alt)
        tx, ty, _ = coord_transform.TransformPoint(ty, tx)
        if num == 0:
            first_x = tx
            first_y = ty
            first_z = tz

        num += 1
        tx -= first_x
        ty = first_y-ty
        tz = tz - first_z

        # 转四元数
        q = euler_to_quaternion(float(gb_yaw), float(gb_pitch), float(gb_roll))
        q_relative = quaternion_multiply(base_q_inv, q)

        qx, qy, qz, qw = q_relative

        line = f"{timestamp:.6f} {tx:.7f} {ty:.7f} {tz:.7f} {qx:.7f} {qy:.7f} {qz:.7f} {qw:.7f}"
        tum_data.append(line)
        timestamp += time_increment

    # 写入输出文件
    try:
        with open(output_file_path, 'w', encoding='utf-8') as out_file:
            out_file.write("\n".join(tum_data))
        print(f"成功提取 {len(tum_data)} 条数据，保存在 {output_file_path}")
    except Exception as e:
        print(f"写入文件时出错: {e}")

if __name__ == "__main__":
    input_srt = '/home/lty/datasets_my/DJI/m300/DJI_0110_6_W.SRT'      # 替换为你的SRT路径
    output_tum = '/home/lty/datasets_my/DJI/m300/DJI_0110_6_W_tum.txt'  # 输出TUM文件路径

    extract_tum_with_quaternion(input_srt, output_tum)
