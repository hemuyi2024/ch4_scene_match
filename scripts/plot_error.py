import matplotlib.pyplot as plt

def plot_errors(error_file, save_path="error_plot.png", y_limit=(-10, 10)):
    """
    从 error_file 中读取 ex、ey、dist 和轨迹长度，并在单个 figure 中绘制三个子图。
    横坐标为轨迹长度，纵坐标分别是 ex、ey、dist 的值（单位：米）。

    参数:
    - error_file: str, error文件的路径。
    - save_path: str, 保存图片的路径，默认为 "error_plot.png"。
    - y_limit: tuple, y 轴的固定范围，默认为 (-10, 10)。
    """
    ex_values = []
    ey_values = []
    dist_values = []
    traj_length_values = []

    # 1. 读取 error 文件
    with open(error_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line_num, line in enumerate(lines, start=1):
            line = line.strip()
            if not line:
                continue
            # 例如： "0, 0.7306, 0.3120, 0.7945, 0.0000"
            parts = line.split(",")
            if len(parts) < 5:
                # 格式不正确则跳过
                print(f"跳过格式不正确的行 {line_num}: {line}")
                continue
            # parts[0] 是 frm_id，后面四个是误差和轨迹长度
            _, ex_str, ey_str, dist_str, traj_length_str = parts
            try:
                ex = float(ex_str)
                ey = float(ey_str)
                dist = float(dist_str)
                traj_length = float(traj_length_str)
            except ValueError:
                # 如果转换失败，可能是脏数据，先跳过
                print(f"跳过无法转换的行 {line_num}: {line}")
                continue

            ex_values.append(ex)
            ey_values.append(ey)
            dist_values.append(dist)
            traj_length_values.append(traj_length)

    if not traj_length_values:
        print("没有有效的数据可绘制。")
        return

    # 2. 准备绘制
    x_axis = traj_length_values

    # 3. 创建一个 figure，3 行 1 列子图
    fig, axs = plt.subplots(nrows=3, ncols=1, figsize=(12, 10), sharex=True)

    # （1）子图1：X 方向误差
    axs[0].plot(x_axis, ex_values, color='blue', label='LonError')
    axs[0].set_ylabel("Longitude Error (m)")
    axs[0].legend(loc='upper right')
    axs[0].grid(True)
    axs[0].set_ylim(y_limit)  # 设置 y 轴范围

    # （2）子图2：Y 方向误差
    axs[1].plot(x_axis, ey_values, color='green', label='LatError')
    axs[1].set_ylabel("Latitude Error (m)")
    axs[1].legend(loc='upper right')
    axs[1].grid(True)
    axs[1].set_ylim(y_limit)  # 设置 y 轴范围

    # （3）子图3：距离误差
    axs[2].plot(x_axis, dist_values, color='red', label='DistanceError')
    axs[2].set_ylabel("Distance Error (m)")
    axs[2].set_xlabel("Trajectory Length (m)")
    axs[2].legend(loc='upper right')
    axs[2].grid(True)
    axs[2].set_ylim(y_limit)  # 设置 y 轴范围

    # 4. 调整布局并保存
    plt.tight_layout()
    plt.savefig(save_path, dpi=600)
    plt.show()

if __name__ == "__main__":
    error_file = "/home/lty/outputs/scene_match_seu_0110_6/error_elevation.txt"
    plot_errors(error_file, save_path="error_plot.png", y_limit=(0,35))
