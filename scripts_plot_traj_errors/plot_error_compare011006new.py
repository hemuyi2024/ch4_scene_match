import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import gridspec
import numpy as np
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset


def parse_error_file(file_path):
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


def get_strict_ylim(elevpnp_file, orbslam_file, margin_ratio=0.05, gap_ratio=0.05):
    _, ex_e, ey_e, dist_e = parse_error_file(elevpnp_file)
    _, ex_o, ey_o, dist_o = parse_error_file(orbslam_file)

    ylims = []
    for elev_vals, orb_vals in zip([ex_e, ey_e, dist_e], [ex_o, ey_o, dist_o]):
        elev_max = max(elev_vals) * (1 + margin_ratio)
        upper_min = elev_max + elev_max * gap_ratio
        orb_max = max(orb_vals) * (1 + margin_ratio)
        ylims.append(((0, elev_max), (upper_min, orb_max)))

    return ylims


def plot_multi_broken_axis_custom_ylim(error_files, save_path="broken_custom_strict.png", labels=None,
                                       elevpnp_file=None, orbslam_file=None):
    if labels is None:
        labels = [f.split("/")[-1].split(".")[0] for f in error_files]

    custom_colors = [
        (0.2, 0.3, 0.8),
        (0.8, 0.2, 0.2),
        (0.1, 0.6, 0.1),
        (0.5, 0.0, 0.5),
    ]

    y_labels = ["East error (m)", "North error (m)", "Positioning error (m)"]

    ylim_pairs = get_strict_ylim(elevpnp_file, orbslam_file)

    fig = plt.figure(figsize=(10, 9))
    outer_gs = gridspec.GridSpec(3, 1, height_ratios=[1, 1, 1], hspace=0.35)

    for i in range(3):
        gs = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=outer_gs[i], height_ratios=[1, 3], hspace=0.05)
        ax_upper = fig.add_subplot(gs[0])
        ax_lower = fig.add_subplot(gs[1], sharex=ax_upper)

        for idx, (file, label, color) in enumerate(zip(error_files, labels, custom_colors)):
            traj, ex, ey, dist = parse_error_file(file)
            data = [ex, ey, dist][i]
            ax_lower.plot(traj, data, label=label, color=color, marker='o', markersize=1, linewidth=2.5)
            ax_upper.plot(traj, data, label=label, color=color, marker='o', markersize=1, linewidth=2.5)

        (lower_min, lower_max), (upper_min, upper_max) = ylim_pairs[i]
        ax_lower.set_ylim((lower_min, lower_max))
        ax_upper.set_ylim((upper_min, upper_max))

        ax_upper.spines['bottom'].set_visible(False)
        ax_lower.spines['top'].set_visible(False)
        ax_upper.tick_params(labelbottom=False)
        ax_upper.tick_params(axis='y', direction='in', labelsize=16)
        ax_lower.tick_params(axis='both', direction='in', labelsize=16)

        d = .015
        kwargs = dict(transform=ax_upper.transAxes, color='k', clip_on=False)
        ax_upper.plot((-d, +d), (-d, +d), **kwargs)
        ax_upper.plot((1 - d, 1 + d), (-d, +d), **kwargs)
        kwargs.update(transform=ax_lower.transAxes)
        ax_lower.plot((-d, +d), (1 - d, 1 + d), **kwargs)
        ax_lower.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)

        ax_lower.set_ylabel(y_labels[i], fontsize=16)
        if i == 2:
            ax_lower.set_xlabel("Trajectory Length (m)", fontsize=16)

        ax_lower.grid(True)
        ax_upper.grid(True)

        if i == 0:
            ax_upper.legend(loc='upper left', frameon=True, edgecolor='black').get_frame().set_linewidth(1.0)

    plt.subplots_adjust(left=0.08, right=0.97, top=0.97, bottom=0.07, hspace=0.25)
    plt.savefig(save_path, dpi=300)
    plt.show()

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

    custom_colors = [
        (0.2, 0.3, 0.8),  # 蓝紫
        (0.5, 0.0, 0.5),  # 紫
        (0.1, 0.6, 0.1),  # 绿
        (0.8, 0.2, 0.2),  # 红
    ]
    assert len(labels) == len(error_files)

    # 创建子图
    fig, axs = plt.subplots(nrows=3, ncols=1, figsize=(10, 9), sharex=True)

    # 初始化误差类型标签
    y_labels = ["East error (m)", "North error (m)", "Positioning error (m)"]

    # 对每个误差文件进行处理
    for idx, (file, label, color) in enumerate(zip(error_files, labels, custom_colors)):
        traj, ex, ey, dist = parse_error_file(file)
        axs[0].plot(traj, ex, label=label, color=color, marker='o', markersize=1, linewidth=2.5)
        axs[1].plot(traj, ey, label=label, color=color, marker='o', markersize=1, linewidth=2.5)
        axs[2].plot(traj, dist, label=label, color=color, marker='o', markersize=1, linewidth=2.5)

    # 设置每个子图参数
    for i in range(3):
        axs[i].set_ylabel(y_labels[i])
        axs[i].grid(True)
        if i == 0:
            legend = axs[i].legend(
                loc='upper left',
                ncol=1,
                frameon=True,
                edgecolor='black'
            )
            legend.get_frame().set_linewidth(1.0)
        axs[i].tick_params(axis='both', direction='in', labelsize=16)

    # 只设置最下面一个 xlabel
    axs[2].set_xlabel("Trajectory Length (m)")




    # 调整间距
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.05)  # 控制子图间距

    plt.savefig(save_path, dpi=300)
    plt.show()

def plot_multi_error_files_jubufangda(error_files, save_path="error_compare.png", y_limit=(0, 20), labels=None):
    num_files = len(error_files)
    if labels is None:
        labels = [f.split("/")[-1].split(".")[0] for f in error_files]

    custom_colors = [
        (0.2, 0.3, 0.8),  # 蓝紫
        (0.5, 0.0, 0.5),  # 紫
        (0.1, 0.6, 0.1),  # 绿
        (0.8, 0.2, 0.2),  # 红
    ]
    assert len(labels) == len(error_files)

    fig, axs = plt.subplots(nrows=3, ncols=1, figsize=(10, 9), sharex=True)
    y_labels = ["East error (m)", "North error (m)", "Positioning error (m)"]

    # 存储 traj 和 dist 以便后续用于 inset
    traj_all, dist_all = [], []

    for idx, (file, label, color) in enumerate(zip(error_files, labels, custom_colors)):
        traj, ex, ey, dist = parse_error_file(file)
        axs[0].plot(traj, ex, label=label, color=color, marker='o', markersize=1, linewidth=2.5)
        axs[1].plot(traj, ey, label=label, color=color, marker='o', markersize=1, linewidth=2.5)
        axs[2].plot(traj, dist, label=label, color=color, marker='o', markersize=1, linewidth=2.5)
        traj_all.append(traj)
        dist_all.append(dist)

    for i in range(3):
        axs[i].set_ylabel(y_labels[i])
        axs[i].grid(True)
        if i == 0:
            legend = axs[i].legend(loc='upper left', ncol=1, frameon=True, edgecolor='black')
            legend.get_frame().set_linewidth(1.0)
        axs[i].tick_params(axis='both', direction='in', labelsize=16)
    axs[2].set_xlabel("Trajectory Length (m)")

    # 添加局部放大图
    # axins = inset_axes(axs[2], width="30%", height="60%", loc='upper right', borderpad=1)
    axins = inset_axes(
        axs[2],
        width=2.6,  # 单位：英寸
        height=1.4,  # 单位：英寸
        loc='center right',
        bbox_to_anchor=(0.75, 0.6),
        bbox_transform=axs[2].transAxes,
        borderpad=0.5
    )
    # 设置放大区域的范围（你可以根据数据调整）
    x1, x2 = 470, 620  # Trajectory 范围
    y1, y2 = 0, 7  # 定位误差范围
    for traj, dist, color in zip(traj_all, dist_all, custom_colors[:len(error_files)]):
        axins.plot(traj, dist, color=color, marker='o', markersize=1, linewidth=2.5)

    axins.set_xlim(x1, x2)
    axins.set_ylim(y1, y2)

    axins.tick_params(labelsize=15)
    axins.tick_params(labelbottom=False, labelleft=False)

    axins.grid(False)

    # 连接放大图和主图
    mark_inset(axs[2], axins, loc1=2, loc2=4, fc="none", ec="0.3", lw=1.5)

    plt.tight_layout()
    plt.subplots_adjust(hspace=0.05)
    plt.savefig(save_path, dpi=300)
    plt.show()
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
        "/home/lty/paper/results/011006/errors/elevpnp.txt",
        "/home/lty/paper/results/011006/errors/slam.txt",
        "/home/lty/paper/results/011006/errors/proposed.txt",
    ]
    labels = ["ElevPnP", "ORB-SLAM3", "Proposed"]

    # plot_multi_broken_axis_custom_ylim(
    #     error_files,
    #     save_path="/home/lty/paper/results/011006/error_compare_broken_strict.png",
    #     labels=labels,
    #     elevpnp_file=error_files[0],
    #     orbslam_file=error_files[1],
    # )

    plot_multi_error_files_jubufangda(error_files, save_path="/home/lty/paper/results/011006/error_compare0603-0613.png",
                           labels=labels)
