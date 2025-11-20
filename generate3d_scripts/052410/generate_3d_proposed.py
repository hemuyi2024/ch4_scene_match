import os

def read_utm_2d(utm_2d_file):
    """
    读取proposed.txt中的二维UTM坐标，返回列表（按行顺序存储）
    列表元素格式：(x, y)
    """
    utm_2d_list = []
    try:
        with open(utm_2d_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    print(f"警告：第 {line_num} 行为空，跳过")
                    continue
                parts = line.split()
                if len(parts) != 2:
                    print(f"警告：第 {line_num} 行格式异常（需2列），内容：{line}，跳过")
                    continue
                x, y = parts
                utm_2d_list.append((x, y))
        print(f"成功读取二维UTM坐标文件，共 {len(utm_2d_list)} 个关键帧")
    except FileNotFoundError:
        print(f"错误：二维UTM文件未找到：{utm_2d_file}")
        exit(1)
    except Exception as e:
        print(f"错误：读取二维UTM文件时异常：{e}")
        exit(1)
    return utm_2d_list


def extract_height_from_tum(tum_file):
    """
    从KeyFrameTrajectoryGeo.txt（TUM格式）中提取高度信息（tz列），返回列表（按行顺序存储）
    """
    height_list = []
    try:
        with open(tum_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    print(f"警告：TUM文件第 {line_num} 行为空，跳过")
                    continue
                parts = line.split()
                if len(parts) != 8:
                    print(f"警告：TUM文件第 {line_num} 行格式异常（需8列），内容：{line}，跳过")
                    continue
                tz = float(parts[3])  # 高度
                height_list.append(tz)
        print(f"成功读取TUM轨迹文件，共提取 {len(height_list)} 个关键帧的高度")
    except FileNotFoundError:
        print(f"错误：TUM轨迹文件未找到：{tum_file}")
        exit(1)
    except Exception as e:
        print(f"错误：读取TUM轨迹文件时异常：{e}")
        exit(1)
    return height_list


def generate_3d_utm(utm_2d_list, height_list, output_file, z_offset=0.0):
    """
    合并二维UTM坐标和高度，生成三维UTM坐标文件
    新增参数 z_offset：对每个高度都加上指定的偏移量
    """
    if len(utm_2d_list) != len(height_list):
        print(f"警告：二维UTM关键帧数量（{len(utm_2d_list)}）与高度数量（{len(height_list)}）不一致！")
        print("将按较少的数量进行合并，多余部分将被忽略")
        min_count = min(len(utm_2d_list), len(height_list))
        utm_2d_list = utm_2d_list[:min_count]
        height_list = height_list[:min_count]

    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"创建输出目录：{output_dir}")

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for idx, ((x, y), height) in enumerate(zip(utm_2d_list, height_list), 1):
                height_adjusted = height + z_offset
                f.write(f"{x} {y} {height_adjusted}\n")
        print(f"成功生成三维UTM坐标文件：{output_file}")
        print(f"共写入 {len(utm_2d_list)} 个关键帧（已加 z_offset={z_offset}）")
    except Exception as e:
        print(f"错误：写入三维UTM文件时异常：{e}")
        exit(1)


if __name__ == "__main__":
    utm_2d_file = '/home/lty/paper/results/052410/traj/proposed.txt'  # 二维UTM坐标
    tum_file = '/home/lty/outputs/seu0524/010/KeyFrameTrajectoryGeo-.txt'  # TUM格式轨迹（含高度）
    output_3d_file = '/home/lty/paper/results/052410/traj0603(3d)/proposed(3d).txt'  # 输出三维坐标
    # ⭐ 在这里设置高度偏移量
    z_offset = 121.27032499  # 例如所有高度 +2.5 米

    utm_2d_list = read_utm_2d(utm_2d_file)
    height_list = extract_height_from_tum(tum_file)
    generate_3d_utm(utm_2d_list, height_list, output_3d_file, z_offset=z_offset)
