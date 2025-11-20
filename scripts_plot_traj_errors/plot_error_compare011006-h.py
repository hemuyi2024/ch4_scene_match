import matplotlib.pyplot as plt

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

def plot_positioning_error(error_files, save_path="positioning_error.png", y_limit=(0, 20), labels=None):
    num_files = len(error_files)
    if labels is None:
        labels = [f.split("/")[-1].split(".")[0] for f in error_files]

    custom_colors = [
        (0.1, 0.6, 0.1),
        (0.8, 0.2, 0.2),
        (0.2, 0.3, 0.8),
        (0.5, 0.0, 0.5),
    ]
    assert len(labels) == len(error_files)

    fig, ax = plt.subplots(figsize=(10, 5))  # 只用一个子图

    for idx, (file, label, color) in enumerate(zip(error_files, labels, custom_colors)):
        traj, _, _, dist = parse_error_file(file)
        ax.plot(traj, dist, label=label, color=color, marker='o', markersize=1, linewidth=2.5)

    ax.set_ylabel("Positioning error (m)", fontsize=16)
    ax.set_xlabel("Trajectory Length (m)", fontsize=16)
    ax.grid(True)
    ax.tick_params(axis='both', direction='in', labelsize=16)
    ax.legend(loc='upper left', frameon=True, edgecolor='black').get_frame().set_linewidth(1.0)

    # if y_limit is not None:
        # ax.set_ylim(y_limit)

    plt.tight_layout()
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
        "/home/lty/paper/results/011006/errors/proposed.txt",
        "/home/lty/paper/results/011006/errors/h.txt",
    ]
    labels = ["Proposed", "Homography-based"]

    plot_positioning_error(
        error_files,
        save_path="/home/lty/paper/results/011006/h_error_compare0603.png",
        y_limit=(0, 100),
        labels=labels
    )
