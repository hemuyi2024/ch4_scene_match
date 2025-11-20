import numpy as np
import plotly.graph_objects as go

def load_trajectory(file_path):
    data = np.loadtxt(file_path)
    return data[:, 0], data[:, 1], data[:, 2]

def plot_trajectories(file_list, legend_labels, output_path=None):
    assert len(file_list) == len(legend_labels), "轨迹数量和图例标签数量不一致！"

    trajectories = []

    # 加载所有轨迹
    for file in file_list:
        x, y, z = load_trajectory(file)
        trajectories.append((x, y, z))

    # 颜色（与 matplotlib 版本一致）
    colors = [
        "gray",         # Ground truth
        "royalblue",    # Elev-PnP
        "purple",       # SLAM
        "green",        # Ours
    ]

    # 创建 3D 图
    fig = go.Figure()

    for (x, y, z), name, color in zip(trajectories, legend_labels, colors):
        fig.add_trace(go.Scatter3d(
            x=x,
            y=y,
            z=z,
            mode='lines',
            name=name,
            line=dict(width=6, color=color),
        ))

    # 设置坐标轴
    fig.update_layout(
        scene=dict(
            xaxis=dict(title="UTM X (m)", nticks=6),
            yaxis=dict(title="UTM Y (m)", nticks=6),
            zaxis=dict(title="Z (m)", nticks=6),

            # 关键！保持真实比例，Plotly 会自动无留白显示
            aspectmode='data',
        ),

        legend=dict(
            x=0.02, y=0.02,
            bgcolor="rgba(255,255,255,0.6)",
            bordercolor="black"
        ),

        margin=dict(l=0, r=0, t=0, b=0),  # 完全无留白
    )

    # 显示到屏幕
    fig.show()

    # 保存为 PNG（可选）
    if output_path is not None:
        fig.write_image(output_path, scale=4)  # scale=4 提高分辨率
        print(f"保存成功：{output_path}")


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
        output_path="/home/lty/paper/results/011006/traj_compare0603_3d_plotly.png"
    )
