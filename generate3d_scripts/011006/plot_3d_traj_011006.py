import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

def load_trajectory(file_path):
    data = np.loadtxt(file_path)
    return data[:, 0], data[:, 1], data[:, 2]

def align_trajectories(ref_xyz, xyz):
    """将轨迹平移，使其起点与参考轨迹起点对齐"""
    dx, dy, dz = ref_xyz[0][0] - xyz[0][0], ref_xyz[1][0] - xyz[1][0], ref_xyz[2][0] - xyz[2][0]
    return xyz[0] + dx, xyz[1] + dy, xyz[2] + dz

def plot_trajectories(file_list, legend_labels, output_path="trajectory_plot_3d.png"):
    assert len(file_list) == len(legend_labels), "轨迹数量和图例标签数量不一致！"

    trajectories = []

    # 加载所有轨迹
    for file in file_list:
        x, y, z = load_trajectory(file)
        trajectories.append((x, y, z))

    # 对齐 SLAM 和 Proposed 起点到 ElevPnP 起点
    elevpnp_xyz = trajectories[1]  # 假设 ElevPnP 是第二个
    for idx in [2, 3]:  # SLAM, Proposed
        trajectories[idx] = align_trajectories(elevpnp_xyz, trajectories[idx])

    # 对齐后更新所有坐标，用于设置轴范围
    all_x, all_y, all_z = [], [], []
    for x, y, z in trajectories:
        all_x.extend(x)
        all_y.extend(y)
        all_z.extend(z)

    # 自定义颜色
    custom_colors = [
        (0.5, 0.5, 0.5),   # Ground truth
        (0.2, 0.3, 0.8),   # Elev-PnP
        (0.5, 0.0, 0.5),   # SLAM
        (0.1, 0.6, 0.1),   # Ours
    ]

    # 创建三维图像
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_proj_type('ortho')

    # 绘制轨迹
    for idx, (x, y, z) in enumerate(trajectories):
        linestyle = '--' if idx == 0 else '-'
        ax.plot(x, y, z, color=custom_colors[idx], linestyle=linestyle,
                label=legend_labels[idx], linewidth=2.4)

    # 坐标范围
    min_x, max_x = min(all_x) - 10, max(all_x) + 10
    min_y, max_y = min(all_y) - 10, max(all_y) + 10
    min_z, max_z = 0, 120

    ax.set_xlim(min_x, max_x)
    ax.set_ylim(min_y, max_y)
    print(min_y, max_y)
    ax.set_zlim(min_z, max_z)

    # 强制等比例显示
    ax.set_box_aspect([
        (max_x - min_x),
        (max_y - min_y),
        (250 - 0)
    ])

    # 坐标轴标签
    ax.set_xlabel("UTM X (m)", fontsize=16, labelpad=20)
    ax.set_ylabel("UTM Y (m)", fontsize=16, labelpad=20)
    ax.set_zlabel("Z (m)", fontsize=16, labelpad=1)

    # 坐标刻度样式
    ax.tick_params(axis='both', labelsize=14, direction='in')
    ax.tick_params(axis='z', labelsize=14, direction='in')

    # 假设 all_y 是轨迹中 Y 的原始值
    yticks = np.linspace(min(all_y), max(all_y), 5)  # 设置 5 个刻度
    ax.set_yticks(yticks)
    ax.set_yticklabels([f"{int(y)}" for y in yticks])


    # 刻度线样式
    for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
        axis._axinfo['tick']['inward_factor'] = 0.0
        axis._axinfo['tick']['outward_factor'] = 0.25
        axis._axinfo['tick']['size'] = 8
        axis._axinfo['tick']['linewidth'] = {True: 1.2, False: 1.0}

    # 设置合理刻度间隔
    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=6))
    # ax.yaxis.set_major_locator(ticker.MaxNLocator(nbins=6))
    ax.zaxis.set_major_locator(ticker.MaxNLocator(nbins=4))

    # 坐标面背景白色
    ax.xaxis.pane.set_facecolor((1, 1, 1, 1))
    ax.yaxis.pane.set_facecolor((1, 1, 1, 1))
    ax.zaxis.pane.set_facecolor((1, 1, 1, 1))
    ax.xaxis.pane.set_edgecolor('w')
    ax.yaxis.pane.set_edgecolor('w')
    ax.zaxis.pane.set_edgecolor('w')

    # 图例
    ax.legend(
        fontsize=16,
        loc='lower center',
        bbox_to_anchor=(0.6, 0.2),
        edgecolor='black',
    )

    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.6)
    ax.view_init(elev=15, azim=-55)
    # plt.tight_layout()
    # plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    plt.savefig(output_path, dpi=300, bbox_inches='tight',pad_inches=0.2)

    # plt.savefig(output_path, dpi=300)
    print(f"✅ 三维轨迹图已保存至：{output_path}")


if __name__ == "__main__":
    trajectory_files = [
        "/home/lty/paper/results/011006/traj0603(3d)/gt(3d).txt",
        "/home/lty/paper/results/011006/traj0603(3d)/elevpnp(3d).txt",
        "/home/lty/paper/results/011006/traj0603(3d)/slam(3d).txt",
        "/home/lty/paper/results/011006/traj0603(3d)/proposed(3d).txt",
    ]

    legend_labels = [
        "GroundTruth",
        "ElevPnP",
        "ORB-SLAM3",
        "Proposed"
    ]

    plot_trajectories(
        trajectory_files,
        legend_labels,
        output_path="/home/lty/paper/results/011006/traj_compare0603_3d.png"
    )