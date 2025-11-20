import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import gridspec
import numpy as np

from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset


# =============================================================
# 解析三维误差文件（Index Ex Ey Ez Dist3D TrajLen）
# =============================================================
def parse_error_file(file_path):
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
                _, ex, ey, ez, dist, traj_len = map(float, parts)

                # --- 核心：全部取绝对值 ---
                ex_vals.append(abs(ex))
                ey_vals.append(abs(ey))
                ez_vals.append(abs(ez))
                dist_vals.append(abs(dist))
                traj_vals.append(traj_len)

            except ValueError:
                print(f"跳过无法解析的行 {line_num}: {line}")
                continue

    return traj_vals, ex_vals, ey_vals, ez_vals, dist_vals



# =============================================================
# 获得断轴范围（严格版本）
# =============================================================
def get_strict_ylim_3d(elev_file, orb_file, margin_ratio=0.05, gap_ratio=0.06):
    _, ex_e, ey_e, ez_e, dist_e = parse_error_file(elev_file)
    _, ex_o, ey_o, ez_o, dist_o = parse_error_file(orb_file)

    ylims = []
    for elev_vals, orb_vals in zip(
        [ex_e, ey_e, ez_e, dist_e],
        [ex_o, ey_o, ez_o, dist_o]
    ):
        elev_max = max(elev_vals) * (1 + margin_ratio)
        upper_min = elev_max + elev_max * gap_ratio
        orb_max = max(orb_vals) * (1 + margin_ratio)

        ylims.append(((0, elev_max), (upper_min, orb_max)))

    return ylims



# =============================================================
# 绘图（断轴版本）——三维误差 + Dist4D
# =============================================================
def plot_multi_broken_axis_3d(error_files, save_path="broken_3d.png",
                              labels=None, elevpnp_file=None, orbslam_file=None):

    if labels is None:
        labels = [f.split("/")[-1].split(".")[0] for f in error_files]

    custom_colors = [
        (0.2, 0.3, 0.8),
        (0.8, 0.2, 0.2),
        (0.1, 0.6, 0.1),
    ]

    y_labels = ["East error (m)", "North error (m)", "Height error (m)", "Positioning error (m)"]

    ylim_pairs = get_strict_ylim_3d(elevpnp_file, orbslam_file)

    fig = plt.figure(figsize=(10, 12))
    outer_gs = gridspec.GridSpec(4, 1, hspace=0.32)

    # 四个误差图：Ex / Ey / Ez / Dist
    for i in range(4):
        gs = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=outer_gs[i],
                                              height_ratios=[1, 3], hspace=0.05)
        ax_upper = fig.add_subplot(gs[0])
        ax_lower = fig.add_subplot(gs[1], sharex=ax_upper)

        for file, label, color in zip(error_files, labels, custom_colors):
            traj, ex, ey, ez, dist = parse_error_file(file)
            data = [ex, ey, ez, dist][i]
            ax_lower.plot(traj, data, label=label, color=color, linewidth=2.4, markersize=1)
            ax_upper.plot(traj, data, label=label, color=color, linewidth=2.4, markersize=1)

        # 设置 ylim
        (lower_min, lower_max), (upper_min, upper_max) = ylim_pairs[i]
        ax_lower.set_ylim((lower_min, lower_max))
        ax_upper.set_ylim((upper_min, upper_max))

        # 断轴效果
        ax_upper.spines['bottom'].set_visible(False)
        ax_lower.spines['top'].set_visible(False)
        ax_upper.tick_params(labelbottom=False)
        d = .015
        kwargs = dict(transform=ax_upper.transAxes, color='k', clip_on=False)
        ax_upper.plot((-d, +d), (-d, +d), **kwargs)
        ax_upper.plot((1 - d, 1 + d), (-d, +d), **kwargs)
        kwargs.update(transform=ax_lower.transAxes)
        ax_lower.plot((-d, +d), (1 - d, 1 + d), **kwargs)
        ax_lower.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)

        # 标签
        ax_lower.set_ylabel(y_labels[i], fontsize=16)
        if i == 3:
            ax_lower.set_xlabel("Trajectory Length (m)", fontsize=16)

        ax_lower.grid(True)
        ax_upper.grid(True)

        if i == 0:
            ax_upper.legend(loc='upper left', frameon=True, edgecolor='black').get_frame().set_linewidth(1.0)

    plt.savefig(save_path, dpi=300)
    plt.show()



# =============================================================
# 三维误差简单对比图（无断轴）
# =============================================================
def plot_multi_error_files_3d(error_files, save_path="error_3d.png", labels=None):

    if labels is None:
        labels = [f.split("/")[-1].split(".")[0] for f in error_files]

    custom_colors = [
        (0.2, 0.3, 0.8),
        (0.5, 0.0, 0.5),
        (0.1, 0.6, 0.1),
    ]

    fig, axs = plt.subplots(nrows=4, ncols=1, figsize=(10, 11), sharex=True)
    y_labels = ["East error (m)", "North error (m)", "Height error (m)", "Positioning error (m)"]

    for file, label, color in zip(error_files, labels, custom_colors):
        traj, ex, ey, ez, dist = parse_error_file(file)
        axs[0].plot(traj, ex, color=color, label=label, linewidth=2.3)
        axs[1].plot(traj, ey, color=color, linewidth=2.3)
        axs[2].plot(traj, ez, color=color, linewidth=2.3)
        axs[3].plot(traj, dist, color=color, label=label, linewidth=2.3)

    for i in range(4):
        axs[i].set_ylabel(y_labels[i])
        axs[i].grid(True)
        axs[i].tick_params(axis='both', direction='in')

        if i == 0:
            axs[i].legend(loc='upper left', frameon=True, edgecolor='black').get_frame().set_linewidth(1.0)

    axs[3].set_xlabel("Trajectory Length (m)")
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.show()



# =============================================================
# 局部放大版本（三维版）
# =============================================================
def plot_multi_error_files_jubufangda_3d(error_files, save_path="error_3d_zoom.png", labels=None):

    if labels is None:
        labels = [f.split("/")[-1].split(".")[0] for f in error_files]

    custom_colors = [
        (0.2, 0.3, 0.8),
        (0.5, 0.0, 0.5),
        (0.1, 0.6, 0.1),
    ]

    fig, axs = plt.subplots(nrows=4, ncols=1, figsize=(10, 12), sharex=True)
    y_labels = ["East error (m)", "North error (m)", "Height error (m)", "Positioning error (m)"]

    traj_all, dist_all = [], []

    for file, label, color in zip(error_files, labels, custom_colors):
        traj, ex, ey, ez, dist = parse_error_file(file)
        axs[0].plot(traj, ex, label=label, color=color, marker='o', markersize=1.5, linewidth=2.5)
        axs[1].plot(traj, ey, label=label, color=color, marker='o', markersize=1.5, linewidth=2.5)
        axs[2].plot(traj, ez, label=label, color=color, marker='o', markersize=1.5, linewidth=2.5)
        axs[3].plot(traj, dist, label=label, color=color, marker='o', markersize=1.5, linewidth=2.5)

        traj_all.append(traj)
        dist_all.append(dist)

    for i in range(4):
        axs[i].set_ylabel(y_labels[i])
        axs[i].grid(True)
        axs[i].tick_params(axis='both', direction='in')
        if i == 0:
            legend = axs[i].legend(loc='upper left', ncol=1, frameon=True, edgecolor='black')
            legend.get_frame().set_linewidth(1.0)

    axs[3].set_xlabel("Trajectory Length (m)")

    # 添加局部放大
    axins = inset_axes(
        axs[2],
        width=2.6,  # 单位：英寸
        height=1.6,  # 单位：英寸
        loc='center right',
        bbox_to_anchor=(0.95, -0.6),
        bbox_transform=axs[2].transAxes,
        borderpad=0.5
    )
    x1, x2 = 400, 500
    y1, y2 = 0, 13

    for traj, dist, color in zip(traj_all, dist_all, custom_colors):
        axins.plot(traj, dist, color=color, linewidth=2.3)

    axins.set_xlim(x1, x2)
    axins.set_ylim(y1, y2)
    axins.tick_params(labelsize=14)
    axins.tick_params(labelbottom=False, labelleft=False)
    mark_inset(axs[3], axins, loc1=2, loc2=4, fc="none", ec="0.3", lw=1)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.show()



# =============================================================
# 主程序示例
# =============================================================
if __name__ == "__main__":
    plt.rcParams.update({
        'font.size': 16,
        'axes.labelsize': 16,
        'xtick.labelsize': 16,
        'ytick.labelsize': 16,
        'legend.fontsize': 16,
    })

    error_files = [
        "/home/lty/paper/results/052409/errors(3d)/error_elevpnp(3d).txt",
        "/home/lty/paper/results/052409/errors(3d)/error_slam(3d).txt",
        "/home/lty/paper/results/052409/errors(3d)/error_proposed(3d).txt",
    ]
    labels = ["ElevPnP", "ORB-SLAM3", "Proposed"]

    plot_multi_error_files_jubufangda_3d(
        error_files,
        save_path="/home/lty/paper/results/052409/error_compare_3d.png",
        labels=labels
    )
