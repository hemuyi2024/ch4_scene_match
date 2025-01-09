from my_pkg.tools import rotate_point_z
def process_trajectory(input_file, output_file):
    # 定义常量
    offset_x = 668622.79564965
    offset_y = 3548240.19051630

    # offset_x = 668641.8187182354
    # offset_y = 3548389.262551563

    # 打开输入文件进行读取
    with open(input_file, 'r') as infile:
        # 打开输出文件进行写入
        with open(output_file, 'w') as outfile:
            for line in infile:
                # 读取每一行并分割成数值
                data = line.split()
                point = [float(data[1]), float(data[2]), 0]
                # 旋转点
                point = rotate_point_z(point, 3.5)
                # 获取 x 和 y 值并进行转换
                try:
                    x = float(data[1]) + offset_x
                    y = offset_y- float(data[2])

                    # x = float(point[0]) + offset_x
                    # y = offset_y- float(point[1])

                    # 将转换后的 x 和 y 写入到输出文件
                    outfile.write(f"{x} {y}\n")
                except ValueError:
                    # 如果某一行数据有问题跳过
                    print(f"Skipping invalid line: {line}")


# 调用函数，传入文件路径
input_file = '/home/lty/code/ORB_SLAM3_detailed_comments/traj/KeyFrameTrajectoryGeo.txt'
output_file = '/home/lty/outputs/scene_match_0103_seu_2/geoKFrame.txt'
process_trajectory(input_file, output_file)

print("Processing complete. Converted data saved to 'geoKFrame.txt'.")
