import open3d as o3d
import numpy as np
from matplotlib import pyplot as plt


def load_3d_points_from_txt(file_path):
    """
    读取卫星三维点（TXT格式）：X Y Z
    """
    points = []
    with open(file_path, 'r') as f:
        header = f.readline()  # 跳过表头
        for line in f:
            try:
                x, y, z = map(float, line.strip().split())
                points.append([x, y, z])
            except:
                continue  # 跳过格式不对的行
    return np.array(points)


def visualize_satellite_3d_txt(txt_path):
    # 读取点数据
    points_3d = load_3d_points_from_txt(txt_path)

    # 创建 Open3D 点云对象
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points_3d)

    # 按高度着色
    z_values = points_3d[:, 2]
    z_min, z_max = z_values.min(), z_values.max()
    norm_z = (z_values - z_min) / (z_max - z_min + 1e-6)  # 归一化
    colors = plt.get_cmap('terrain')(norm_z)[:, :3]  # colormap 返回 RGBA，这里取 RGB
    pcd.colors = o3d.utility.Vector3dVector(colors)

    # 创建坐标轴
    max_range = np.max(points_3d, axis=0) - np.min(points_3d, axis=0)
    axis_size = np.max(max_range) * 0.05
    coordinate_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(
        size=axis_size, origin=[0, 0, 0])

    # 网格地面显示
    ground_z = np.percentile(z_values, 95)
    min_bound = np.min(points_3d, axis=0)
    max_bound = np.max(points_3d, axis=0)
    grid = o3d.geometry.LineSet.create_from_axis_aligned_bounding_box(
        o3d.geometry.AxisAlignedBoundingBox(
            min_bound=[min_bound[0], min_bound[1], ground_z - 0.5],
            max_bound=[max_bound[0], max_bound[1], ground_z + 0.1]
        ))
    grid.paint_uniform_color([0.5, 0.5, 0.5])

    # 可视化窗口
    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name='Satellite 3D Map', width=1280, height=800)

    vis.add_geometry(pcd)
    vis.add_geometry(coordinate_frame)
    vis.add_geometry(grid)

    render_option = vis.get_render_option()
    render_option.point_size = 5
    render_option.background_color = np.array([1, 1, 1])

    ctr = vis.get_view_control()
    ctr.set_front([0, -1, 0.5])
    ctr.set_up([0, 0, 1])
    ctr.set_lookat([0, 0, 0])
    ctr.set_zoom(0.8)

    vis.run()
    vis.destroy_window()


if __name__ == '__main__':
    txt_path = "/home/lty/ch4/output_elevation/satellite_3d_final.txt"
    visualize_satellite_3d_txt(txt_path)
