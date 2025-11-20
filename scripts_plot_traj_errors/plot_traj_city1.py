import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import os
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset

plt.rcParams['font.sans-serif'] = 'SimHei'  # 设置全局字体为 Arial
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

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
    min_x, max_x = min(all_x) , max(all_x)
    min_y, max_y = min(all_y) , max(all_y)

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
    xrange = max_x - min_x
    yrange = max_y - min_y
    plt.xlim(min_x, max_x)  # 增加5%的边距
    plt.ylim(min_y, max_y)
    ax = plt.gca()
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):d}'))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f'{int(y):d}'))
    plt.tick_params(axis='both', direction='in', labelsize=16)

    ax.xaxis.set_major_locator(ticker.MultipleLocator(250))  # 每50米一格
    ax.yaxis.set_major_locator(ticker.MultipleLocator(150))

    # 标注与图例
    plt.xlabel("UTM X (m)", fontsize=16)
    plt.ylabel("UTM Y (m)", fontsize=16)
    # plt.legend(fontsize=16, loc='best', bbox_to_anchor=(0.2, 0.5),edgecolor='black',)#011006
    plt.legend(fontsize=16, loc='upper right',edgecolor='black',)
    plt.grid(True)
    plt.axis('equal')
    plt.tight_layout()

    # ✅ 添加局部放大图
    axins = inset_axes(ax, width=1.4, height=2, loc='lower left', borderpad=1)

    # 设置放大区域范围（根据你想关注的区域设置）
    x1, x2 = 12123800, 12123870  # UTM X 范围
    y1, y2 = 4062050, 4062150  # UTM Y 范围
    axins.set_xlim(x1, x2)
    axins.set_ylim(y1, y2)

    # 在局部图中重绘轨迹
    for idx, (x, y) in enumerate(trajectories):
        linestyle = '--' if idx == 0 else '-'
        axins.plot(x, y, color=custom_colors[idx], linestyle=linestyle, linewidth=2.4)

    axins.tick_params(axis='both', labelsize=10, direction='in',left = False, right = False, labelleft=False, labelbottom=False)
    axins.grid(False)
    axins.set_xticks([])
    axins.set_yticks([])
    axins.tick_params(left=False, right=False, bottom=False, top=False)

    # 加上主图与局部图连线
    mark_inset(ax, axins, loc1=2, loc2=4, fc="none", ec="black", linewidth=1.0)

    # 保存图像
    plt.savefig(output_path, dpi=300)
    print(f"图像保存至：{output_path}")

if __name__ == "__main__":
    trajectory_files = [
        #052409
        "/home/lty/paper/results/city1/traj0602/gt.txt",
        "/home/lty/paper/results/city1/traj0602/elevpnp.txt",
        "/home/lty/paper/results/city1/traj0602/orb-slam3.txt",
        "/home/lty/paper/results/city1/traj0602/proposed.txt",

        #052409-h
    ]

    legend_labels = [
        "真值",
        "ElevPnP",
        "ORB-SLAM3",
        "所提算法"
    ]

    plot_trajectories(
        trajectory_files,
        legend_labels,
        output_path="/home/lty/paper/results/city1/traj_compare0602_cn.png"
    )
