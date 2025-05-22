import os
import numpy as np

# 输入轨迹文件列表（只含 x y）
input_files = [
    "/home/lty/论文/results/city1/GroundTruth.txt",
    "/home/lty/论文/results/city1/match.txt",
    "/home/lty/论文/results/city1/slam.txt",
    "/home/lty/论文/results/city1/elevation.txt",
    "/home/lty/论文/results/city1/proposed.txt",
]

# 参考的 TUM 轨迹文件（含完整信息）
reference_file = "/home/lty/outputs/RealUAV/city1/KeyFrameTrajectoryGeo.txt"

# 输出目录
output_dir = "/home/lty/论文/results/city1/traj_tum"
os.makedirs(output_dir, exist_ok=True)

def load_reference_tum(file_path):
    """
    加载参考 TUM 文件，返回列表：[(t, x, y, z, qx, qy, qz, qw), ...]
    """
    ref_data = []
    with open(file_path, "r") as f:
        for line in f:
            if not line.strip():
                continue
            parts = list(map(float, line.strip().split()))
            if len(parts) != 8:
                raise ValueError(f"参考轨迹格式错误: {line}")
            ref_data.append(parts)
    return ref_data

def load_xy(file_path):
    """
    加载输入轨迹文件，只包含 x, y
    """
    data = np.loadtxt(file_path)
    if data.ndim == 1:
        data = np.expand_dims(data, axis=0)
    return data[:, 0], data[:, 1]

def save_tum_format(output_path, ref_data, x_list, y_list):
    """
    用 x, y 替换参考数据中的 x, y，保存为 TUM 格式
    """
    with open(output_path, "w") as f:
        for i, (t, _, _, z, qx, qy, qz, qw) in enumerate(ref_data):
            if i >= len(x_list):
                break
            x = x_list[i]
            y = y_list[i]
            f.write(f"{t:.6f} {x:.7f} {y:.7f} {z:.7f} {qx:.7f} {qy:.7f} {qz:.7f} {qw:.7f}\n")

def main():
    ref_data = load_reference_tum(reference_file)

    for input_file in input_files:
        x_list, y_list = load_xy(input_file)
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_path = os.path.join(output_dir, f"{base_name}_tum.txt")
        save_tum_format(output_path, ref_data, x_list, y_list)
        print(f"已生成: {output_path}")

if __name__ == "__main__":
    main()
