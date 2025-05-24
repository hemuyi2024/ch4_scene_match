from PIL.ImageChops import offset

from my_pkg.tools import rotate_point_z
def process_trajectory(input_file, output_file):



    # 定义常量 city3
    #city1
    # offset_x = 12123905.77494114
    # offset_y = 4061590.61553926
    #city3
    # offset_x = 12117477.47634211
    # offset_y = 4055168.53057232

    # offset_x = 668641.8187182354
    # offset_y = 3548389.262551563

    #011006
    offset_x = 668627.38021085
    offset_y = 3548190.77141221

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
input_file = '/home/lty/outputs/seu0524/009/KeyFrameTrajectory.txt'
output_file = '/home/lty/paper/results/052409/ORB-SLAM3.txt'
process_trajectory(input_file, output_file)

print("Processing complete. Converted data saved to 'geoKFrame.txt'.")
