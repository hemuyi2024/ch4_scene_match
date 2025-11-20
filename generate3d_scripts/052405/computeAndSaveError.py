import os
from math import sqrt

def load_xyz_file(file_path):
    """读取 txt 文件中的三维坐标，格式：x y z"""
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 3:
                continue
            x, y, z = map(float, parts)
            data.append((x, y, z))
    return data


def compute_errors(gt, pred):
    """
    计算单条预测轨迹和真值轨迹的误差
    返回误差列表 results，每项为：
    (index, ex, ey, ez, dist_3d, flight_dist)
    """
    assert len(gt) == len(pred), "预测轨迹与真值轨迹长度不一致！"

    results = []
    flight_dist_accum = 0.0
    last_gt_x, last_gt_y, last_gt_z = gt[0]

    for i, ((x_gt, y_gt, z_gt), (x_p, y_p, z_p)) in enumerate(zip(gt, pred)):

        # 误差
        ex = x_p - x_gt
        ey = y_p - y_gt
        ez = z_p - z_gt
        dist_3d = sqrt(ex*ex + ey*ey + ez*ez)

        # 计算真实飞行距离（累积）
        if i == 0:
            flight_dist_accum = 0.0
        else:
            dx = x_gt - last_gt_x
            dy = y_gt - last_gt_y
            dz = z_gt - last_gt_z
            d = sqrt(dx*dx + dy*dy + dz*dz)
            flight_dist_accum += d

        last_gt_x, last_gt_y, last_gt_z = x_gt, y_gt, z_gt

        results.append((i, ex, ey, ez, dist_3d, flight_dist_accum))

    return results


def save_error_file(output_path, results):
    """保存结果到 txt 文件"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("Index Ex Ey Ez Dist3D FlightDist\n")
        for (idx, ex, ey, ez, dist_3d, fd) in results:
            f.write(f"{idx} {ex:.4f} {ey:.4f} {ez:.4f} {dist_3d:.4f} {fd:.4f}\n")


def process_one_prediction(gt_file, pred_file, output_file):
    """处理单个预测文件"""
    gt = load_xyz_file(gt_file)
    pred = load_xyz_file(pred_file)

    print(f"加载 gt：{len(gt)} 条，pred：{len(pred)} 条")

    results = compute_errors(gt, pred)
    save_error_file(output_file, results)

    print(f"误差文件已保存: {output_file}\n")


if __name__ == "__main__":

    gt_file = "/home/lty/paper/results/052409/traj0603(3d)/gt(3d)_minus8.txt"

    pred_files = [
        "/home/lty/paper/results/052409/traj0603(3d)/elevpnp(3d).txt",
        "/home/lty/paper/results/052409/traj0603(3d)/proposed(3d).txt",
        "/home/lty/paper/results/052409/traj0603(3d)/slam(3d).txt"
    ]

    output_files = [
        "/home/lty/paper/results/052409/errors(3d)/error_elevpnp(3d).txt",
        "/home/lty/paper/results/052409/errors(3d)/error_proposed(3d).txt",
        "/home/lty/paper/results/052409/errors(3d)/error_slam(3d).txt"
    ]

    for pred_file, out_file in zip(pred_files, output_files):
        process_one_prediction(gt_file, pred_file, out_file)
