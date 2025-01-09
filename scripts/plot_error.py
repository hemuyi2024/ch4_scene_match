import matplotlib.pyplot as plt


def plot_errors(error_file, save_path="error_plot.png", y_limit=(-10, 10)):
    """
    从 error_file 中读取 ex、ey、dist，并在单个 figure 中绘制三个子图。
    横坐标为点的索引 0 ~ (N-1)，纵坐标分别是 ex、ey、dist 的值（单位：米）。

    参数:
    - error_file: str, 错误文件的路径。
    - save_path: str, 保存图片的路径，默认为 "error_plot.png"。
    - y_limit: tuple, y 轴的固定范围，默认为 (-10, 10)。
    """
    ex_values = []
    ey_values = []
    dist_values = []

    # 1. 读取 error 文件
    with open(error_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # 例如： "12, 0.5412, 1.2583, 1.3655"
            parts = line.split(",")
            if len(parts) < 4:
                # 格式不正确则跳过
                continue
            # parts[0] 是 frm_id，后面三个是误差
            _, ex_str, ey_str, dist_str = parts
            try:
                ex = float(ex_str)
                ey = float(ey_str)
                dist = float(dist_str)
            except ValueError:
                # 如果转换失败，可能是脏数据，先跳过
                continue

            ex_values.append(ex)
            ey_values.append(ey)
            dist_values.append(dist)

    # 2. 准备绘制
    x_axis = range(len(ex_values))

    # 3. 创建一个 figure，3 行 1 列子图
    fig, axs = plt.subplots(nrows=3, ncols=1, figsize=(10, 8), sharex=True)

    # （1）子图1：X 方向误差
    axs[0].plot(x_axis, ex_values, color='blue', label='ErrorX')
    axs[0].set_ylabel("X Error (m)")
    axs[0].legend(loc='upper right')
    axs[0].grid(True)
    axs[0].set_ylim(y_limit)  # 设置 y 轴范围

    # （2）子图2：Y 方向误差
    axs[1].plot(x_axis, ey_values, color='green', label='ErrorY')
    axs[1].set_ylabel("Y Error (m)")
    axs[1].legend(loc='upper right')
    axs[1].grid(True)
    axs[1].set_ylim(y_limit)  # 设置 y 轴范围

    # （3）子图3：距离误差
    axs[2].plot(x_axis, dist_values, color='red', label='Distance Error')
    axs[2].set_ylabel("Distance (m)")
    axs[2].set_xlabel("Index (0 ~ N-1)")
    axs[2].legend(loc='upper right')
    axs[2].grid(True)
    axs[2].set_ylim(y_limit)  # 设置 y 轴范围

    # 4. 调整布局并保存
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.show()


if __name__ == "__main__":
    error_file = "/home/lty/outputs/scene_match_0103_seu_2/error.txt"
    plot_errors(error_file, save_path="error_plot.png", y_limit=(0, 10))
