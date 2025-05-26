import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import os

def load_trajectory(file_path):
    data = np.loadtxt(file_path)
    return data[:, 0], data[:, 1]

def plot_trajectories(file_list, legend_labels, output_path="trajectory_plot.png"):
    assert len(file_list) == len(legend_labels), "轨迹数量和图例标签数量不一致！"

    all_x = []
    all_y = []
    trajectories = []

    # 加载所有轨迹数据
    for file in file_list:
        x, y = load_trajectory(file)
        all_x.extend(x)
        all_y.extend(y)
        trajectories.append((x, y))

    # 设置坐标范围
    min_x, max_x = min(all_x) - 1, max(all_x) + 1
    min_y, max_y = min(all_y) - 1, max(all_y) + 1

    # 自定义颜色
    custom_colors = [
        (0.5, 0.5, 0.5),   # Ground truth
        (0.2, 0.3, 0.8),   # Elev-PnP
        (0.5, 0.0, 0.5),   # SLAM
        (0.1, 0.6, 0.1),   # Ours
        (0.8, 0.2, 0.2),   # Ours (alternative)
        (0.9, 0.5, 0.1),   # Ours (alternative)
        (0.1, 0.1, 0.1),   # Ours (alternative)
        (0.8, 0.8, 0.8)    # Ours (alternative)
    ]

    # 开始绘图
    plt.figure(figsize=(10, 7))
    for idx, (x, y) in enumerate(trajectories):
        linestyle = '--' if idx == 0 else '-'  # 第一个轨迹是 GT，用虚线
        plt.plot(x, y, color=custom_colors[idx], linestyle=linestyle,
                 label=legend_labels[idx], linewidth=2.4)

    # 坐标格式设置
    plt.xlim(min_x, max_x)
    plt.ylim(min_y, max_y)
    ax = plt.gca()
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):d}'))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f'{int(y):d}'))
    plt.tick_params(axis='both', direction='in', labelsize=16)

    # 标注与图例
    plt.xlabel("UTM X (m)", fontsize=16)
    plt.ylabel("UTM Y (m)", fontsize=16)
    # plt.legend(fontsize=16, loc='best', bbox_to_anchor=(0.2, 0.5),edgecolor='black',)#011006
    plt.legend(fontsize=16, loc='upper left',edgecolor='black',)
    plt.grid(True)
    plt.axis('equal')
    plt.tight_layout()

    # 保存图像
    plt.savefig(output_path, dpi=300)
    print(f"图像保存至：{output_path}")

if __name__ == "__main__":
    trajectory_files = [
        #052409
        "/home/lty/paper/results/052410/traj/groundtruth.txt",
        "/home/lty/paper/results/052410/traj/elevpnp2.0.txt",
        "/home/lty/paper/results/052410/traj/orb-slam3.txt",
        "/home/lty/paper/results/052410/traj/proposed.txt",

        #052409-h
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
        output_path="/home/lty/paper/results/052410/traj_compare2.0.png"
    )
