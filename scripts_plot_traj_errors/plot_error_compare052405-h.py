import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import gridspec

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

def plot_broken_axis(error_files, save_path="broken_error.png", labels=None):
    if labels is None:
        labels = [f.split("/")[-1].split(".")[0] for f in error_files]

    custom_colors = [
        (0.1, 0.6, 0.1),
        (0.8, 0.2, 0.2),
        (0.2, 0.3, 0.8),
        (0.5, 0.0, 0.5),
    ]
    assert len(labels) == len(error_files)

    fig = plt.figure(figsize=(10, 5))
    gs = gridspec.GridSpec(2, 1, height_ratios=[1, 2], hspace=0.05)

    ax_upper = fig.add_subplot(gs[0])
    ax_lower = fig.add_subplot(gs[1], sharex=ax_upper)

    # 设置断轴位置（例如下部显示0-25，上部显示60以上）
    lower_ylim = (0, 65)
    upper_ylim = (65, 270)

    for idx, (file, label, color) in enumerate(zip(error_files, labels, custom_colors)):
        traj, _, _, dist = parse_error_file(file)
        ax_lower.plot(traj, dist, label=label, color=color, marker='o', markersize=1, linewidth=2.5)
        ax_upper.plot(traj, dist, label=label, color=color, marker='o', markersize=1, linewidth=2.5)

    # 设置坐标轴范围
    ax_lower.set_ylim(lower_ylim)
    ax_upper.set_ylim(upper_ylim)

    # 去除上图的 x 轴刻度
    ax_upper.tick_params(labelbottom=False)
    ax_upper.tick_params(axis='y', direction='in', labelsize=16)
    ax_lower.tick_params(axis='both', direction='in', labelsize=16)

    ax_lower.set_xlabel("Trajectory Length (m)", fontsize=16)
    ax_lower.set_ylabel("Positioning error (m)", fontsize=16)

    # 添加“断裂”符号
    d = .015  # 断口大小
    kwargs = dict(transform=ax_upper.transAxes, color='k', clip_on=False)
    ax_upper.plot((-d, +d), (-d, +d), **kwargs)
    ax_upper.plot((1 - d, 1 + d), (-d, +d), **kwargs)

    kwargs.update(transform=ax_lower.transAxes)
    ax_lower.plot((-d, +d), (1 - d, 1 + d), **kwargs)
    ax_lower.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)

    # 网格与图例
    ax_lower.grid(True)
    ax_upper.grid(True)
    ax_upper.legend(loc='upper left', frameon=True, edgecolor='black').get_frame().set_linewidth(1.0)

    # plt.tight_layout()
    # subplot
    # parameters:
    # left = 0.08566666666666667
    # right = 0.9698853870370927
    # bottom = 0.16083333333333333
    # top = 0.952
    # wspace = 0.2
    # hspace = 0.2
    plt.subplots_adjust(left=0.08566666666666667, right=0.9698853870370927, top=0.952, bottom=0.16083333333333333,
                        wspace=0.2,hspace=0.2)  # 更像原图边距

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
        "/home/lty/paper/results/052405/error_files/error_proposed.txt",
        "/home/lty/paper/results/052405/errors/h.txt",
    ]
    labels = ["Proposed", "Homography-based"]

    plot_broken_axis(
        error_files,
        save_path="/home/lty/paper/results/052405/h_error_compare0603.png",
        labels=labels
    )
