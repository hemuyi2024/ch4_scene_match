import os

def parse_keyframe_file(file_path):
    """解析KeyFrameId.txt，获取关键帧ID到帧ID的映射（使用你提供的方法）"""
    keyframe_mapping = {}
    try:
        with open(file_path, "r") as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split(",")
                    keyframe_id = int(parts[0].split(":")[1].strip())
                    frame_id = int(parts[1].split(":")[1].strip())
                    keyframe_mapping[keyframe_id] = frame_id
        print(f"成功解析关键帧映射文件，共 {len(keyframe_mapping)} 个关键帧")
    except FileNotFoundError:
        print(f"关键帧映射文件未找到: {file_path}")
    except Exception as e:
        print(f"解析关键帧映射文件时出错: {e}")
    return keyframe_mapping

def build_frame_to_3d_mapping(gt3d_file_path):
    """建立帧ID到三维坐标（经度, 纬度, 绝对高度）的映射"""
    frame_3d_mapping = {}
    try:
        with open(gt3d_file_path, 'r', encoding='utf-8') as f:
            for frame_id, line in enumerate(f):  # 行号即帧ID（从0开始）
                line = line.strip()
                if not line:
                    continue
                parts = [x.strip() for x in line.split(",")]
                if len(parts) != 3:
                    print(f"警告：第 {frame_id} 帧的三维坐标格式异常: {line}")
                    continue
                lon, lat, abs_alt = parts
                frame_3d_mapping[frame_id] = abs_alt  # 只需要绝对高度
        print(f"成功建立帧ID到绝对高度的映射，共 {len(frame_3d_mapping)} 个帧")
    except FileNotFoundError:
        print(f"三维坐标文件未找到: {gt3d_file_path}")
    except Exception as e:
        print(f"读取三维坐标文件时出错: {e}")
    return frame_3d_mapping

def read_utm_2d(utm_2d_file):
    """读取二维UTM坐标，返回 {关键帧ID: (x, y)} 映射"""
    utm_2d_mapping = {}
    try:
        with open(utm_2d_file, 'r', encoding='utf-8') as f:
            # 假设gt.txt的行顺序与关键帧ID的自然顺序一致（即使ID不连续）
            # 例如：第1行对应keyframe_mapping中最小的ID，第2行对应次小的ID，以此类推
            keyframe_ids = sorted(keyframe_mapping.keys())  # 按关键帧ID升序排列
            for idx, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                if idx >= len(keyframe_ids):
                    print(f"警告：UTM文件行数超过关键帧数量，忽略多余行: {line}")
                    continue
                keyframe_id = keyframe_ids[idx]  # 按排序后的关键帧ID关联
                x, y = line.split()
                utm_2d_mapping[keyframe_id] = (x, y)
        print(f"成功读取二维UTM坐标，共 {len(utm_2d_mapping)} 条记录")
    except FileNotFoundError:
        print(f"二维UTM文件未找到: {utm_2d_file}")
    except Exception as e:
        print(f"读取二维UTM文件时出错: {e}")
    return utm_2d_mapping

def extend_utm_to_3d(keyframe_mapping, frame_3d_mapping, utm_2d_mapping, output_3d_file):
    """将二维UTM扩展为三维（严格按keyframe_mapping中的映射关系）"""
    output_dir = os.path.dirname(output_3d_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"创建输出目录: {output_dir}")

    try:
        with open(output_3d_file, 'w', encoding='utf-8') as out_f:
            # 按关键帧ID升序处理，保证输出顺序与UTM文件一致
            for keyframe_id in sorted(keyframe_mapping.keys()):
                # 检查是否有对应的UTM坐标
                if keyframe_id not in utm_2d_mapping:
                    print(f"警告：关键帧 {keyframe_id} 未找到对应的二维UTM坐标，跳过")
                    continue
                x, y = utm_2d_mapping[keyframe_id]

                # 获取对应的帧ID
                frame_id = keyframe_mapping[keyframe_id]

                # 获取对应的绝对高度
                if frame_id not in frame_3d_mapping:
                    print(f"警告：帧ID {frame_id}（对应关键帧 {keyframe_id}）未找到高度，跳过")
                    continue
                abs_alt = frame_3d_mapping[frame_id]

                # 写入三维坐标
                out_f.write(f"{x} {y} {abs_alt}\n")

        print(f"成功将二维UTM扩展为三维，结果保存在: {output_3d_file}")
    except Exception as e:
        print(f"扩展UTM坐标时出错: {e}")

if __name__ == "__main__":
    # 文件路径
    gt3d_all_file = '/home/lty/outputs/scene_match_seu_0110_6/gt3d(all_10hz).txt'
    keyframe_file = '/home/lty/outputs/scene_match_seu_0110_6/KeyFrameId.txt'
    utm_2d_file = '/home/lty/paper/results/011006/traj0603/gt.txt'
    output_3d_file = '/home/lty/paper/results/011006/traj0603(3d)/gt3d.txt'

    # 1. 解析关键帧映射（{关键帧ID: 帧ID}）
    keyframe_mapping = parse_keyframe_file(keyframe_file)
    if not keyframe_mapping:
        print("关键帧映射关系为空，无法继续")
        exit(1)

    # 2. 建立帧ID到绝对高度的映射
    frame_3d_mapping = build_frame_to_3d_mapping(gt3d_all_file)
    if not frame_3d_mapping:
        print("帧ID到高度的映射为空，无法继续")
        exit(1)

    # 3. 读取二维UTM并关联关键帧ID（按关键帧ID排序）
    utm_2d_mapping = read_utm_2d(utm_2d_file)
    if not utm_2d_mapping:
        print("二维UTM坐标为空，无法继续")
        exit(1)

    # 4. 扩展为三维并保存
    extend_utm_to_3d(keyframe_mapping, frame_3d_mapping, utm_2d_mapping, output_3d_file)