import numpy as np
import os

# ============================================================
# 加载三维坐标
# ============================================================
def load_xyz(file_path):
    data = np.loadtxt(file_path)
    return data  # shape (N,3)


# ============================================================
# TUM 标准误差计算：2D / 3D 欧式距离
# ============================================================
def compute_metrics(est, gt, use_3d=False):
    """
    est: (N,3)
    gt : (N,3)
    use_3d: False → 使用 (x,y)
             True  → 使用 (x,y,z)
    """
    if use_3d:
        diff = est - gt
        errors = np.linalg.norm(diff, axis=1)           # 欧式距离 √(dx² + dy² + dz²)
    else:
        diff_xy = est[:, :2] - gt[:, :2]
        errors = np.linalg.norm(diff_xy, axis=1)        # √(dx² + dy²)

    metrics = {
        "Max error":  np.max(errors),
        "Min error":  np.min(errors),
        "Mean error": np.mean(errors),
        "RMSE":       np.sqrt(np.mean(errors ** 2)),
        "Std":        np.std(errors)
    }
    return metrics


# ============================================================
# 主函数
# ============================================================
if __name__ == "__main__":

    # ======= 修改为你的文件路径 =======
    gt_file = "/home/lty/paper/results/052409/traj0603(3d)/gt(3d)_minus8.txt"
    est_file1 = "/home/lty/paper/results/052409/traj0603(3d)/slam(3d).txt"
    est_file2 = "/home/lty/paper/results/052409/traj0603(3d)/elevpnp(3d).txt"
    est_file3 = "/home/lty/paper/results/052409/traj0603(3d)/proposed(3d).txt"
    # =================================

    gt = load_xyz(gt_file)
    est1 = load_xyz(est_file1)
    est2 = load_xyz(est_file2)
    est3 = load_xyz(est_file3)

    all_results = {
        os.path.basename(est_file1): est1,
        os.path.basename(est_file2): est2,
        os.path.basename(est_file3): est3,
    }

    for name, est in all_results.items():
        print("\n=====================================")
        print(f"{name} — 2D 误差 (x,y)")
        print("=====================================")
        m2 = compute_metrics(est, gt, use_3d=False)
        for k, v in m2.items():
            print(f"{k}: {v:.4f} m")

        print("\n-------------------------------------")
        print(f"{name} — 3D 误差 (x,y,z)")
        print("-------------------------------------")
        m3 = compute_metrics(est, gt, use_3d=True)
        for k, v in m3.items():
            print(f"{k}: {v:.4f} m")
