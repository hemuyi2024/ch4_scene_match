import matplotlib.pyplot as plt

def parse_error_file(file_path):
    """
    解析一个误差文件，返回 ex, ey, dist, traj_len 四个序列
    """
    ex_vals, ey_vals, dist_vals, traj_vals = [], [], [], []

    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",")
            if len(parts) < 5:
                print(f"跳过格式不正确的行 {line_num}: {line}")
                continue
            try:
                _, ex, ey, dist, traj_len = map(float, parts)
                ex_vals.append(ex)
                ey_vals.append(ey)
                dist_vals.append(dist)
                traj_vals.append(traj_len)
            except ValueError:
                print(f"跳过无法解析的行 {line_num}: {line}")
                continue

    return traj_vals, ex_vals, ey_vals, dist_vals


def plot_multi_error_files(error_files, save_path="error_compare.png", y_limit=(0, 20), labels=None):
    """
    绘制多个误差文件的对比图（每类误差一个子图），每个数据点标记圆圈
    参数：
        error_files: List[str]，误差文件路径
        save_path: str，图像保存路径
        y_limit: tuple，y轴范围
        labels: List[str]，可选，图例名称（默认为文件名）
    """
    num_files = len(error_files)
    if labels is None:
        labels = [f.split("/")[-1].split(".")[0] for f in error_files]

    colors = ['blue', 'green', 'red', 'orange', 'purple', 'brown']  # 最多6个源，足够
    custom_colors = [
        (0.4, 0.4, 0.4),  #
        (1.0, 0.5, 0.0),
        (0.8, 0.2, 0.2),
        (0.1, 0.7, 0.1),
    ]
    assert len(labels) == len(error_files)

    # 创建子图
    fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(30, 8), sharex=True)

    # 初始化误差类型标签
    y_labels = ["East error(m)", "North error(m)", "Positioning error(m)"]

    # 对每个误差文件进行处理
    for idx, (file, label, color) in enumerate(zip(error_files, labels, custom_colors)):
        traj, ex, ey, dist = parse_error_file(file)
        axs[0].plot(traj, ex, label=label, color=color, marker='o', markersize=8, linewidth=1.5)
        axs[1].plot(traj, ey, label=label, color=color, marker='o', markersize=8, linewidth=1.5)
        axs[2].plot(traj, dist, label=label, color=color, marker='o', markersize=8, linewidth=1.5)

    # 设置三个子图的参数
    for i in range(3):
        axs[i].set_ylabel(y_labels[i])
        axs[i].grid(True)
        axs[i].set_ylim(y_limit)
        legend = axs[i].legend(
            loc='upper left',
            bbox_to_anchor=(0.0, 1.0),  # 从 1.05 调整到 1.02
            ncol=len(labels),
            frameon=True,
            edgecolor='black'
        )
        legend.get_frame().set_linewidth(1.0)
        axs[i].tick_params(axis='both', direction='in', labelsize=17)

    axs[0].set_xlabel("Trajectory Length (m)")
    axs[1].set_xlabel("Trajectory Length (m)")
    axs[2].set_xlabel("Trajectory Length (m)")
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.show()


if __name__ == "__main__":
    # 设置全局字体大小和字体
    plt.rcParams.update({
        'font.size': 20,  # 控制整体字号
        'axes.titlesize': 18,  # 子图标题字号
        'axes.labelsize': 18,  # x/y轴标签字号
        'xtick.labelsize': 18,  # x轴刻度字号
        'ytick.labelsize': 18,  # y轴刻度字号
        'legend.fontsize': 16,  # 图例字号
    })
    # 指定误差文件路径
    error_files = [
        "/home/lty/outputs/RealUAV/city1/error_match.txt",
        "/home/lty/outputs/RealUAV/city1/error_elevation.txt",
        "/home/lty/outputs/RealUAV/city1/error_proposed(slam).txt",
        "/home/lty/outputs/RealUAV/city1/error_proposed.txt",
    ]

    # 自定义图例名称（将作为图例显示内容）
    labels = ["match", "elevation", "slam", "proposed"]

    plot_multi_error_files(error_files, save_path="error_compare.png", y_limit=(0, 32), labels=labels)
