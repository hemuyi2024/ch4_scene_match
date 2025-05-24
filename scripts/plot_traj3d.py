import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.ticker as ticker
import numpy as np
import os

def load_trajectory_3d(file_path):
    data = np.loadtxt(file_path)
    return data[:, 0], data[:, 1], data[:, 2]

def plot_3d_trajectories(file_list, output_path="trajectory_3d_plot.png"):
    all_x, all_y, all_z = [], [], []
    trajectories = []
    labels = []

    # 加载所有轨迹
    for file in file_list:
        x, y, z = load_trajectory_3d(file)
        all_x.extend(x)
        all_y.extend(y)
        all_z.extend(z)
        trajectories.append((x, y, z))
        labels.append(os.path.splitext(os.path.basename(file))[0])

    # 设置边界范围，并增加适当留白
    margin = 1
    min_x, max_x = min(all_x) - margin, max(all_x) + margin
    min_y, max_y = min(all_y) - margin, max(all_y) + margin
    min_z, max_z = min(all_z) - margin, max(all_z) + margin

    # 创建3D图像
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # 自定义颜色
    custom_colors = [
        # (0.6, 0.6, 0.6),     # 灰色（第一条通常为真值）
        (0.1, 0.7, 0.1),     # 绿色
        (1.0, 0.5, 0.0),     # 橙色
        (0.8, 0.2, 0.2),     # 红色
        (0.4, 0.4, 0.4),     # 深灰
        (0.3, 0.3, 0.9),     # 蓝紫
    ]

    for idx, (x, y, z) in enumerate(trajectories):
        if idx == 0:
            ax.plot(x, y, z, color=custom_colors[0], linestyle='-', linewidth=2, label=labels[idx])
        else:
            color = custom_colors[idx % len(custom_colors)]
            ax.plot(x, y, z, color=color, linewidth=2, label=labels[idx])

    # 设置坐标轴范围
    ax.set_xlim(min_x, max_x)
    ax.set_ylim(min_y, max_y)
    ax.set_zlim(min_z, max_z)

    # 设置坐标轴标签与字体大小
    ax.set_xlabel("UTM X (m)", fontsize=15)
    ax.set_ylabel("UTM Y (m)", fontsize=15)
    ax.set_zlabel("Elevation (m)", fontsize=15)

    # 设置坐标轴刻度格式（整型、不使用科学计数法）
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x)}'))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f'{int(y)}'))
    ax.zaxis.set_major_formatter(ticker.FuncFormatter(lambda z, _: f'{int(z)}'))
    ax.tick_params(labelsize=12)

    # 图例自动避让轨迹
    ax.legend(fontsize=13, loc='best', framealpha=0.6)

    # 使坐标轴比例尽量一致
    def set_axes_equal(ax):
        ranges = [max_x - min_x, max_y - min_y, max_z - min_z]
        max_range = max(ranges) / 2.0
        mid_x = (max_x + min_x) * 0.5
        mid_y = (max_y + min_y) * 0.5
        mid_z = (max_z + min_z) * 0.5
        ax.set_xlim(mid_x - max_range, mid_x + max_range)
        ax.set_ylim(mid_y - max_range, mid_y + max_range)
        ax.set_zlim(mid_z - max_range, mid_z + max_range)

    set_axes_equal(ax)

    # 网格 & 布局
    ax.grid(True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=600)
    print(f"3D轨迹图保存至：{output_path}")

if __name__ == "__main__":
    # 修改为你实际的轨迹文件路径
    trajectory_files = [
        "/home/lty/paper/results/011006/elevation3d.txt",
    ]
    plot_3d_trajectories(trajectory_files, output_path="/home/lty/paper/results/011006/traj_compare_3d.png")
