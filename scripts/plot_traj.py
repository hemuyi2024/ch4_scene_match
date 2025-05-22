import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import os

def load_trajectory(file_path):
    data = np.loadtxt(file_path)
    return data[:, 0], data[:, 1]

def plot_trajectories(file_list, output_path="trajectory_plot.png"):
    all_x = []
    all_y = []
    trajectories = []
    labels = []

    # 加载所有轨迹
    for file in file_list:
        x, y = load_trajectory(file)
        all_x.extend(x)
        all_y.extend(y)
        trajectories.append((x, y))
        labels.append(os.path.splitext(os.path.basename(file))[0])

    # 计算边界范围，增加10m边距
    min_x, max_x = min(all_x) - 10, max(all_x) + 10
    min_y, max_y = min(all_y) - 10, max(all_y) + 10

    # 设置颜色
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'cyan', 'brown']
    custom_colors = [
        (0.4, 0.4, 0.4),  #
        (1.0, 0.5, 0.0),
        (0.8, 0.2, 0.2),
        (0.1, 0.7, 0.1),
    ]

    # 开始绘图
    plt.figure(figsize=(10, 10))
    for idx, (x, y) in enumerate(trajectories):
        if idx == 0:
            # 第一个轨迹：真值，灰色虚线
            plt.plot(x, y, color=(0.6,0.6,0.6), linestyle='--', label=labels[idx], linewidth=2)
        else:
            plt.plot(x, y, color=custom_colors[idx-1], label=labels[idx], linewidth=2)

    # 设置坐标轴范围为实际坐标，并留白
    plt.xlim(min_x, max_x)
    plt.ylim(min_y, max_y)

    # 设置坐标轴格式：不使用科学计数法、不显示小数点
    ax = plt.gca()
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):d}'))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f'{int(y):d}'))
    plt.tick_params(axis='both', direction='in', labelsize=17)

    # 添加图例和样式
    plt.xlabel("UTM X (m)", fontsize=18)
    plt.ylabel("UTM Y (m)", fontsize=18)
    # plt.title("Trajectories", fontsize=18)
    # plt.legend()
    plt.legend(fontsize=16, loc='upper right')
    plt.grid(True)
    plt.axis('equal')
    plt.tight_layout()

    # 保存图像
    plt.savefig(output_path, dpi=600)
    print(f"图像保存至：{output_path}")

if __name__ == "__main__":
    # 这里填入你的轨迹文件路径
    trajectory_files = [
        "/home/lty/论文/results/city1/GroundTruth.txt",
        "/home/lty/论文/results/city1/match.txt",
        "/home/lty/论文/results/city1/slam.txt",
        "/home/lty/论文/results/city1/elevation.txt",
        "/home/lty/论文/results/city1/proposed.txt",
        # 可以继续添加更多轨迹
    ]
    plot_trajectories(trajectory_files, output_path="/home/lty/论文/results/city1/traj.png")
