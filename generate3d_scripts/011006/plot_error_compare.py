import matplotlib.pyplot as plt


def parse_error_file(file_path):
    """
    解析新版误差文件（空格分隔）:
    Index Ex Ey Ez Dist3D FlightDist
    返回：traj_len(FlightDist), |ex|, |ey|, |ez|, |dist|
    """
    traj_vals, ex_vals, ey_vals, ez_vals, dist_vals = [], [], [], [], []

    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split()
            if len(parts) < 6:
                print(f"跳过格式不正确的行 {line_num}: {line}")
                continue
            try:
                index = float(parts[0])
                ex = abs(float(parts[1]))
                ey = abs(float(parts[2]))
                ez = abs(float(parts[3]))
                dist = abs(float(parts[4]))
                traj_len = float(parts[5])

                ex_vals.append(ex)
                ey_vals.append(ey)
                ez_vals.append(ez)
                dist_vals.append(dist)
                traj_vals.append(traj_len)

            except ValueError:
                print(f"跳过无法解析的行 {line_num}: {line}")
                continue

    return traj_vals, ex_vals, ey_vals, ez_vals, dist_vals



# =============================================================
# 绘图（无断轴版本）
# =============================================================
def plot_multi_error_files_4d(error_files, save_path="error_compare.png", labels=None):
    """
    绘制包含 EX / EY / EZ / DIST 四类误差的对比图
    """

    if labels is None:
        labels = [f.split("/")[-1].split(".")[0] for f in error_files]

    custom_colors = [
        (0.2, 0.3, 0.8),
        (0.5, 0.0, 0.5),
        (0.1, 0.6, 0.1),
        (0.8, 0.2, 0.2),
    ]

    assert len(labels) == len(error_files)

    fig, axs = plt.subplots(nrows=4, ncols=1, figsize=(10, 12), sharex=True)

    y_labels = ["East error (m)", "North error (m)", "Height error (m)", "Positioning error (m)"]

    # 绘制
    for idx, (file, label, color) in enumerate(zip(error_files, labels, custom_colors)):
        traj, ex, ey, ez, dist = parse_error_file(file)
        axs[0].plot(traj, ex, label=label, color=color, marker='o', markersize=1.5, linewidth=2.5)
        axs[1].plot(traj, ey, label=label, color=color, marker='o', markersize=1.5, linewidth=2.5)
        axs[2].plot(traj, ez, label=label, color=color, marker='o', markersize=1.5, linewidth=2.5)
        axs[3].plot(traj, dist, label=label, color=color, marker='o', markersize=1.5, linewidth=2.5)

    # 设置子图格式
    for i in range(4):
        axs[i].set_ylabel(y_labels[i])
        axs[i].grid(True)
        if i == 0:
            legend = axs[i].legend(loc='upper left', frameon=True, edgecolor='black')
            legend.get_frame().set_linewidth(1.0)
        axs[i].tick_params(axis='both', direction='in')

    axs[3].set_xlabel("Trajectory Length (m)")

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.show()



# =============================================================
# 主程序
# =============================================================
if __name__ == "__main__":
    plt.rcParams.update({
        'font.size': 16,
        'axes.titlesize': 16,
        'axes.labelsize': 16,
        'xtick.labelsize': 16,
        'ytick.labelsize': 16,
        'legend.fontsize': 16,
    })

    error_files = [
        "/home/lty/paper/results/011006/errors(3d)/error_elevpnp(3d).txt",
        "/home/lty/paper/results/011006/errors(3d)/error_slam(3d).txt",
        "/home/lty/paper/results/011006/errors(3d)/error_proposed(3d).txt",
    ]

    labels = ["ElevPnP", "ORB-SLAM3", "Proposed"]

    plot_multi_error_files_4d(
        error_files,
        save_path="/home/lty/paper/results/011006/error_compare_3D.png",
        labels=labels
    )
