import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset
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
        (0.2, 0.3, 0.8),  #
        (0.5, 0.0, 0.5),
        (0.1, 0.6, 0.1),
        (0.8, 0.2, 0.2),
    ]
    assert len(labels) == len(error_files)

    # 创建子图
    fig, axs = plt.subplots(nrows=3, ncols=1, figsize=(10, 8), sharex=True)#30 8

    # 初始化误差类型标签
    y_labels = ["East error(m)", "North error(m)", "Positioning error(m)"]

    # 对每个误差文件进行处理
    for idx, (file, label, color) in enumerate(zip(error_files, labels, custom_colors)):
        traj, ex, ey, dist = parse_error_file(file)
        axs[0].plot(traj, ex, label=label, color=color, marker='o', markersize=1, linewidth=2.5)
        axs[1].plot(traj, ey, label=label, color=color, marker='o', markersize=1, linewidth=2.5)
        axs[2].plot(traj, dist, label=label, color=color, marker='o', markersize=1, linewidth=2.5)

    # 设置三个子图的参数
    # 设置三个子图的参数
    # for i in range(3):
    #     axs[i].set_ylabel(y_labels[i])
    #     axs[i].grid(True)
    #     # axs[i].set_ylim(y_limit)
    #     if i == 1:
    #         legend = axs[i].legend(
    #             loc='upper left',
    #             # bbox_to_anchor=(0.3, 0.5),  # 从 1.05 调整到 1.02
    #             ncol=1,
    #             frameon=True,
    #             edgecolor='black'
    #         )
    #         legend.get_frame().set_linewidth(1.0)
    #         # axs[i].set_ylim(y_limit)
    #     axs[i].tick_params(axis='both', direction='in', labelsize=16)
    #     axs[i].tick_params(labelbottom=True)  # ← 强制显示x轴刻度
        # if i == 2:
        #     # 添加局部放大图 (e.g., 放大 200m ~ 400m 段)
        #     axins = inset_axes(axs[2], width=1.3, height=1.3, loc="center", borderpad=2)
        #
        #     # 设置放大区域范围
        #     x1, x2 = 0, 200  # 横坐标范围：轨迹长度
        #     y1, y2 = 0, 52  # 纵坐标范围：误差范围
        #     axins.set_xlim(x1, x2)
        #     axins.set_ylim(y1, y2)
        #     axins.set_xticks([])
        #     axins.set_yticks([])
        #     axins.tick_params(left=False, right=False, bottom=False, top=False)
        #
        #     # 绘制局部区域的所有曲线（和 axs[2] 一致）
        #     for file, label, color in zip(error_files, labels, custom_colors):
        #         traj, ex, ey, dist = parse_error_file(file)
        #         axins.plot(traj, dist, label=label, color=color, marker='o', markersize=1, linewidth=2.5)
        #
        #     # 去掉局部图刻度标签（可选）
        #     axins.tick_params(axis='both', direction = 'in',labelsize=10)
        #
        #     # 在主图中标出放大区域
        #     mark_inset(axs[2], axins, loc1=2, loc2=4, fc="none", ec="gray", lw=1.0)

    # axs[2].set_ylim((0,50))

    for i in range(3):
        axs[i].set_ylabel(y_labels[i])
        axs[i].grid(True)
        if i == 0:
            legend = axs[i].legend(loc='upper left', ncol=1, frameon=True, edgecolor='black')
            legend.get_frame().set_linewidth(1.0)
        axs[i].tick_params(axis='both', direction='in', labelsize=16)
    axs[2].set_xlabel("Trajectory Length (m)")
    # axs[0].set_xlabel("Trajectory Length (m)")
    # axs[1].set_xlabel("Trajectory Length (m)")
    axs[2].set_xlabel("Trajectory Length (m)")
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.05)
    # plt.subplots_adjust(wspace=0.3)  # 或其他你觉得合适的值
    plt.savefig(save_path, dpi=300)
    plt.show()


if __name__ == "__main__":
    # 设置全局字体大小和字体
    plt.rcParams.update({
        'font.size': 16,  # 控制整体字号
        'axes.titlesize': 16,  # 子图标题字号
        'axes.labelsize': 16,  # x/y轴标签字号
        'xtick.labelsize': 16,  # x轴刻度字号
        'ytick.labelsize': 16,  # y轴刻度字号
        'legend.fontsize': 16,  # 图例字号
    })
    # 指定误差文件路径
    error_files = [
        # 011006
        # "/home/lty/paper/results/011006/errors/error_elevation.txt",
        # "/home/lty/paper/results/011006/errors/error_ORB-SLAM3.txt",
        # "/home/lty/paper/results/011006/errors/error_proposed.txt",

        "/home/lty/paper/results/city3/errors/elevpnp.txt",
        "/home/lty/paper/results/city3/errors/slam.txt",
        "/home/lty/paper/results/city3/errors/proposed.txt",
    ]

    # 自定义图例名称（将作为图例显示内容）
    labels = ["ElevPnP", "ORB-SLAM3","Proposed"]

    plot_multi_error_files(error_files, save_path="/home/lty/paper/results/city3/error_compare0613.png", y_limit=(0, 100), labels=labels)
