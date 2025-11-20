import os

def parse_keyframe_file(file_path):
    """
    解析KeyFrameId.txt，获取关键帧ID到帧ID的映射（复用之前的方法）
    文件格式示例：keyframe: 0, frame: 10；keyframe: 1, frame: 25 等
    """
    keyframe_mapping = {}
    try:
        with open(file_path, "r") as f:
            for line in f:
                if line.strip():  # 跳过空行
                    parts = line.strip().split(",")
                    # 解析关键帧ID和帧ID（格式：keyframe: X 或 frame: Y）
                    keyframe_id = int(parts[0].split(":")[1].strip())
                    frame_id = int(parts[1].split(":")[1].strip())
                    keyframe_mapping[keyframe_id] = frame_id
        print(f"成功解析关键帧映射文件，共 {len(keyframe_mapping)} 个关键帧")
    except FileNotFoundError:
        print(f"错误：关键帧映射文件未找到：{file_path}")
        exit(1)
    except Exception as e:
        print(f"错误：解析关键帧映射文件时异常：{e}")
        exit(1)
    return keyframe_mapping

def build_frame_to_height_mapping(elev3d_file_path):
    """
    读取elevpnp3d.txt，建立帧ID到高度的映射
    elevpnp3d.txt格式：每行是 三维坐标（UTM X, UTM Y, 高度），行号=帧ID（从0开始）
    """
    frame_height_mapping = {}
    try:
        with open(elev3d_file_path, 'r', encoding='utf-8') as f:
            for frame_id, line in enumerate(f):  # 行号直接作为帧ID
                line = line.strip()
                if not line:
                    print(f"警告：elevpnp3d.txt 第 {frame_id} 帧为空，跳过")
                    continue
                parts = line.split()
                if len(parts) != 3:
                    print(f"警告：elevpnp3d.txt 第 {frame_id} 帧格式异常（需3列），内容：{line}，跳过")
                    continue
                height = parts[2]  # 第3列是高度
                frame_height_mapping[frame_id] = height
        print(f"成功建立帧ID到高度的映射，共 {len(frame_height_mapping)} 个帧")
    except FileNotFoundError:
        print(f"错误：三维坐标文件未找到：{elev3d_file_path}")
        exit(1)
    except Exception as e:
        print(f"错误：读取三维坐标文件时异常：{e}")
        exit(1)
    return frame_height_mapping

def read_utm_2d(utm_2d_file_path):
    """
    读取elevpnp.txt中的二维UTM坐标，返回列表（按行顺序存储，与关键帧顺序一致）
    列表元素格式：(x, y)
    """
    utm_2d_list = []
    try:
        with open(utm_2d_file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    print(f"警告：elevpnp.txt 第 {line_num} 行为空，跳过")
                    continue
                parts = line.split()
                if len(parts) != 2:
                    print(f"警告：elevpnp.txt 第 {line_num} 行格式异常（需2列），内容：{line}，跳过")
                    continue
                x, y = parts
                utm_2d_list.append((x, y))
        print(f"成功读取二维UTM坐标，共 {len(utm_2d_list)} 个关键帧")
    except FileNotFoundError:
        print(f"错误：二维UTM文件未找到：{utm_2d_file_path}")
        exit(1)
    except Exception as e:
        print(f"错误：读取二维UTM文件时异常：{e}")
        exit(1)
    return utm_2d_list

def generate_3d_utm(keyframe_mapping, frame_height_mapping, utm_2d_list, output_file):
    """
    合并二维UTM坐标和高度，生成三维UTM坐标文件
    逻辑：关键帧顺序（elevpnp.txt行顺序）→ 关键帧ID（排序后）→ 帧ID → 高度
    """
    # 检查关键帧数量是否匹配（elevpnp.txt行数 与 关键帧映射数量）
    if len(utm_2d_list) != len(keyframe_mapping):
        print(f"警告：二维UTM关键帧数量（{len(utm_2d_list)}）与关键帧映射数量（{len(keyframe_mapping)}）不一致！")
        print("将按较少的数量进行合并，多余部分将被忽略")
        min_count = min(len(utm_2d_list), len(keyframe_mapping))
        utm_2d_list = utm_2d_list[:min_count]
        # 按关键帧ID升序截取前min_count个
        sorted_keyframe_ids = sorted(keyframe_mapping.keys())[:min_count]
        keyframe_mapping = {k: keyframe_mapping[k] for k in sorted_keyframe_ids}
    else:
        sorted_keyframe_ids = sorted(keyframe_mapping.keys())

    # 确保输出目录存在
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"创建输出目录：{output_dir}")

    # 写入三维UTM坐标（按elevpnp.txt的行顺序）
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for idx, ((x, y), keyframe_id) in enumerate(zip(utm_2d_list, sorted_keyframe_ids), 1):
                # 根据关键帧ID获取帧ID
                frame_id = keyframe_mapping[keyframe_id]
                # 根据帧ID获取高度
                if frame_id not in frame_height_mapping:
                    print(f"警告：帧ID {frame_id}（对应关键帧 {keyframe_id}）未找到高度，跳过")
                    continue
                height = frame_height_mapping[frame_id]
                # 写入格式：UTM X UTM Y 高度
                f.write(f"{x} {y} {height}\n")
        print(f"成功生成三维UTM坐标文件：{output_file}")
        print(f"共写入 {len([1 for k in sorted_keyframe_ids if keyframe_mapping[k] in frame_height_mapping])} 个关键帧的三维坐标")
    except Exception as e:
        print(f"错误：写入三维UTM文件时异常：{e}")
        exit(1)

if __name__ == "__main__":
    # 定义文件路径
    keyframe_file = '/home/lty/outputs/scene_match_seu_0110_6/KeyFrameId.txt'  # 关键帧映射
    utm_2d_file = '/home/lty/paper/results/011006/traj0603/elevpnp.txt'  # 二维UTM坐标
    elev3d_file = '/home/lty/paper/results/011006/elevpnp3d.txt'  # 所有帧的三维坐标（含高度）
    output_3d_file = '/home/lty/paper/results/011006/traj0603(3d)/elevpnp(3d).txt'  # 输出文件

    # 步骤1：解析关键帧映射（关键帧ID→帧ID）
    keyframe_mapping = parse_keyframe_file(keyframe_file)

    # 步骤2：建立帧ID到高度的映射
    frame_height_mapping = build_frame_to_height_mapping(elev3d_file)

    # 步骤3：读取二维UTM坐标（elevpnp.txt）
    utm_2d_list = read_utm_2d(utm_2d_file)

    # 步骤4：生成三维UTM坐标文件
    generate_3d_utm(keyframe_mapping, frame_height_mapping, utm_2d_list, output_3d_file)