import re

def extract_lat_lon_alt_from_srt(srt_file_path, output_file_path):
    """
    从给定的SRT文件中提取所有经纬度和绝对高度信息，并保存到输出文件中。

    :param srt_file_path: 输入的SRT文件路径
    :param output_file_path: 输出的TXT文件路径
    """
    try:
        with open(srt_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"文件未找到: {srt_file_path}")
        return
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return

    # 修复正则表达式：严格匹配 [rel_alt: ... abs_alt: ...] 结构
    # 确保捕获绝对高度（abs_alt）的值
    pattern = re.compile(
        r'\[latitude:\s*([-+]?\d+\.\d+)\]\s*'  # 纬度（带小数点的数值）
        r'\[longitude:\s*([-+]?\d+\.\d+)\]\s*'  # 经度（带小数点的数值）
        r'\[rel_alt:\s*[-+]?\d+\.\d+\s+abs_alt:\s*([-+]?\d+\.\d+)\]',  # 绝对高度（带小数点的数值）
        re.IGNORECASE
    )

    # 查找所有匹配的经纬度和绝对高度信息
    matches = pattern.findall(content)

    if not matches:
        print("未找到任何经纬度和高度信息。")
        return

    # 格式化信息，格式为：经度, 纬度, 绝对高度
    lat_lon_alt_list = [f"{lon}, {lat}, {abs_alt}"
                      for lat, lon, abs_alt in matches]

    try:
        with open(output_file_path, 'w', encoding='utf-8') as out_file:
            id = 0
            for info in lat_lon_alt_list:
                if id % 3 == 0:  # 保持每3条取1条的逻辑
                    out_file.write(info + '\n')
                id += 1
        print(f"成功提取 {len(lat_lon_alt_list)} 条经纬度和绝对高度信息，保存在 {output_file_path}")
    except Exception as e:
        print(f"写入文件时出错: {e}")

if __name__ == "__main__":
    input_srt = '/home/lty/datasets_my/DJI/m300/DJI_20250524070852_0009_W.SRT'
    output_txt = '/home/lty/outputs/seu0524/009/gt3d(all_10hz).txt'
    extract_lat_lon_alt_from_srt(input_srt, output_txt)