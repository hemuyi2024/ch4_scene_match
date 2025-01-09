import os
import re
from my_pkg.tools import parse_keyframe_file

def create_pairs(uav_dir, tif_dir, pairs_file, mappings):
    """
    根据指定的编号范围映射关系，创建 pairs.txt 文件。

    参数：
    - uav_dir: 无人机图片的文件夹路径
    - tif_dir: TIF 影像的文件夹路径
    - pairs_file: 输出的 pairs.txt 文件路径
    - mappings: 一个列表，每个元素是一个字典，包含：
        - 'start_num': 起始无人机图片编号（整数）
        - 'end_num': 结束无人机图片编号（整数）
        - 'tif_name': 对应的 TIF 影像文件名
    """
    # 检查文件夹是否存在
    if not os.path.isdir(uav_dir):
        print(f"无人机图片文件夹不存在：{uav_dir}")
        return
    if not os.path.isdir(tif_dir):
        print(f"TIF 影像文件夹不存在：{tif_dir}")
        return

    # 获取无人机图片和 TIF 影像的文件名列表
    uav_images = os.listdir(uav_dir)
    tif_images = set(os.listdir(tif_dir))  # 使用集合加快查找速度

    # 用于存储匹配结果
    pairs = []

    # 预编译正则表达式，提取无人机图片编号
    pattern = re.compile(r'(\d+)\.\w+$')

    # 遍历无人机图片，解析编号并匹配对应的 TIF 影像
    for uav_img in uav_images:
        match = pattern.match(uav_img)
        if match:
            img_num = int(match.group(1))
            # 查找该编号属于哪个范围
            matched = False
            for mapping in mappings:
                if mapping['start_num'] <= img_num <= mapping['end_num']:
                    tif_name = mapping['tif_name']
                    if tif_name in tif_images:
                        uav_img_path = os.path.join("seu_uav_0103_2/",uav_img)
                        tif_file_path = os.path.join("seu_tif_m300/",tif_name)
                        pairs.append((uav_img_path, tif_file_path))
                        matched = True
                        break  # 找到匹配的范围，退出内层循环
                    else:
                        print(f"TIF 影像文件不存在：{tif_name}")
                        matched = True  # 即使 TIF 文件不存在，也不需要继续检查其他范围
                        break
            if not matched:
                print(f"无人机图片 {uav_img} 未找到对应的 TIF 影像范围。")
        else:
            print(f"无法解析无人机图片的编号：{uav_img}")
    pairs.sort(key=lambda x: x[0])  # 按无人机图片文件名排序
    # 将匹配结果写入 pairs.txt 文件
    with open(pairs_file, 'w') as f:
        for uav_img, tif_name in pairs:
            line = f"{uav_img} {tif_name}\n"
            f.write(line)
    print(f"已生成 pairs.txt 文件：{pairs_file}")

if __name__ == "__main__":
    # 无人机图片文件夹路径
    uav_directory = "/home/lty/datasets_my/DJI/m300/seu_uav_0103_2"
    # TIF 影像文件夹路径
    tif_directory = "/home/lty/datasets_my/DJI/m300/seu_tif_m300"
    # 输出的 pairs.txt 文件路径
    pairs_txt_path = "/home/lty/outputs/scene_match_0103_seu_2/pairs_m300.txt"

    # 指定编号范围映射关系 11-21-dji0200
    mappings_0103_2 = [
        {
            'start_num': 0,
            'end_num': 250,
            'tif_name': '22_0_4500.tif'
        },
        {
            'start_num': 251,
            'end_num': 370,
            'tif_name': '16_1500_3000.tif'
        },
        {
            'start_num': 371,
            'end_num': 490,
            'tif_name': '17_3000_3000.tif'
        },
        {
            'start_num': 491,
            'end_num': 600,
            'tif_name': '11_4500_1500.tif'
        },
        {
            'start_num': 601,
            'end_num': 662,
            'tif_name': '4_4500_0.tif'
        },
        {
            'start_num': 663,
            'end_num': 925,
            'tif_name': '5_6000_0.tif'
        },
        {
            'start_num': 926,
            'end_num': 985,
            'tif_name': '4_4500_0.tif'
        },
        {
            'start_num': 986,
            'end_num': 1095,
            'tif_name': '3_3000_0.tif'
        },
        {
            'start_num': 1096,
            'end_num': 1185,
            'tif_name': '2_1500_0.tif'
        },
        {
            'start_num': 1186,
            'end_num': 1249,
            'tif_name': '1_0_0.tif'
        },
    ]
    mappings_0103_3 = [
        {
            'start_num': 0,
            'end_num': 235,
            'tif_name': '8_0_1500.tif'
        },
        {
            'start_num': 236,
            'end_num': 316,
            'tif_name': '9_1500_1500.tif'
        },
        {
            'start_num': 317,
            'end_num': 377,
            'tif_name': '16_1500_3000.tif'
        },
        {
            'start_num': 378,
            'end_num': 520,
            'tif_name': '17_3000_3000.tif'
        },
        {
            'start_num': 521,
            'end_num': 610,
            'tif_name': '25_4500_4500.tif'
        },
        {
            'start_num': 611,
            'end_num': 690,
            'tif_name': '26_6000_4500.tif'
        },
        {
            'start_num': 691,
            'end_num': 975,
            'tif_name': '33_6000_6000.tif'
        },
        {
            'start_num': 976,
            'end_num': 1080,
            'tif_name': '32_4500_6000.tif'
        },
        {
            'start_num': 1081,
            'end_num': 1150,
            'tif_name': '31_3000_6000.tif'
        },
        {
            'start_num': 1151,
            'end_num': 1250,
            'tif_name': '30_1500_6000.tif'
        },
        {
            'start_num': 1251,
            'end_num': 1660,
            'tif_name': '29_0_6000.tif'
        },
        {
            'start_num': 1661,
            'end_num': 1750,
            'tif_name': '22_0_4500.tif'
        },
        {
            'start_num': 1751,
            'end_num': 1880,
            'tif_name': '15_0_3000.tif'
        },
        {
            'start_num': 1881,
            'end_num': 2010,
            'tif_name': '8_0_1500.tif'
        },
        {
            'start_num': 2011,
            'end_num': 2116,
            'tif_name': '1_0_0.tif'
        },
    ]
    mappings_12_26_m300 = [
        {
            'start_num': 0,
            'end_num': 200,
            'tif_name': '1_0_0.tif'
        },
        {
            'start_num': 201,
            'end_num': 320,
            'tif_name': '8_0_1500.tif'
        },
        {
            'start_num': 321,
            'end_num': 450,
            'tif_name': '15_0_3000.tif'
        },
        {
            'start_num': 451,
            'end_num': 600,
            'tif_name': '22_0_4500.tif'
        },
        {
            'start_num': 601,
            'end_num': 640,
            'tif_name': '23_1500_4500.tif'
        },
        {
            'start_num': 641,
            'end_num': 750,
            'tif_name': '30_1500_6000.tif'
        },
        {
            'start_num': 751,
            'end_num': 850,
            'tif_name': '31_3000_6000.tif'
        },
        {
            'start_num': 851,
            'end_num': 930,
            'tif_name': '32_4500_6000.tif'
        },
        {
            'start_num': 931,
            'end_num': 1060,
            'tif_name': '33_6000_6000.tif'
        },
        {
            'start_num': 1061,
            'end_num': 1150,
            'tif_name': '34_7500_6000.tif'
        },
        {
            'start_num': 1151,
            'end_num': 1280,
            'tif_name': '27_7500_4500.tif'
        },
        {
            'start_num': 1281,
            'end_num': 1380,
            'tif_name': '20_7500_3000.tif'
        },
        {
            'start_num': 1381,
            'end_num': 1500,
            'tif_name': '13_7500_1500.tif'
        },
        {
            'start_num': 1501,
            'end_num': 1560,
            'tif_name': '13_7500_1500.tif'
        },
        {
            'start_num': 1561,
            'end_num': 1660,
            'tif_name': '5_6000_0.tif'
        },
        {
            'start_num': 1661,
            'end_num': 1770,
            'tif_name': '4_4500_0.tif'
        },
        {
            'start_num': 1771,
            'end_num': 1860,
            'tif_name': '3_3000_0.tif'
        },
        {
            'start_num': 1861,
            'end_num': 1950,
            'tif_name': '2_1500_0.tif'
        },
        {
            'start_num': 1951,
            'end_num': 2167,
            'tif_name': '1_0_0.tif'
        },
    ]
    mappings_12_26 = [
        {
            'start_num': 0,
            'end_num': 300,
            'tif_name': '2_2000_0.tif'
        },
        {
            'start_num': 301,
            'end_num': 450,
            'tif_name': '12_2000_2000.tif'
        },
        {
            'start_num': 451,
            'end_num': 600,
            'tif_name': '22_2000_4000.tif'
        },
        {
            'start_num': 601,
            'end_num': 740,
            'tif_name': '33_4000_6000.tif'
        },
        {
            'start_num': 741,
            'end_num': 850,
            'tif_name': '34_6000_6000.tif'
        },
        {
            'start_num': 851,
            'end_num': 910,
            'tif_name': '35_8000_6000.tif'
        },
        {
            'start_num': 911,
            'end_num': 1000,
            'tif_name': '36_10000_6000.tif'
        },
        {
            'start_num': 1001,
            'end_num': 1150,
            'tif_name': '37_12000_6000.tif'
        },
        {
            'start_num': 1151,
            'end_num': 1190,
            'tif_name': '38_14000_6000.tif'
        },
        {
            'start_num': 1191,
            'end_num': 1290,
            'tif_name': '28_14000_4000.tif'
        },
        {
            'start_num': 1291,
            'end_num': 1390,
            'tif_name': '18_14000_2000.tif'
        },
        {
            'start_num': 1391,
            'end_num': 1480,
            'tif_name': '8_14000_0.tif'
        },
        {
            'start_num': 1481,
            'end_num': 1500,
            'tif_name': '7_12000_0.tif'
        },
    ]
    mappings = [
        {
            'start_num': 0,
            'end_num': 234,
            'tif_name': '2_2000_0.tif'
        },
        {
            'start_num': 235,
            'end_num': 346,
            'tif_name': '12_2000_2000.tif'
        },
        {
            'start_num': 347,
            'end_num': 438,
            'tif_name': '22_2000_4000.tif'
        },
        {
            'start_num': 439,
            'end_num': 539,
            'tif_name': '32_2000_6000.tif'
        },
        {
            'start_num': 540,
            'end_num': 679,
            'tif_name': '33_4000_6000.tif'
        },
        {
            'start_num': 680,
            'end_num': 760,
            'tif_name': '34_6000_6000.tif'
        },
        {
            'start_num': 761,
            'end_num': 860,
            'tif_name': '35_8000_6000.tif'
        },
        {
            'start_num': 861,
            'end_num': 940,
            'tif_name': '36_10000_6000.tif'
        },
        {
            'start_num': 941,
            'end_num': 1100,
            'tif_name': '37_12000_6000.tif'
        },
        {
            'start_num': 1101,
            'end_num': 1180,
            'tif_name': '27_12000_4000.tif'
        },
        {
            'start_num': 1181,
            'end_num': 1280,
            'tif_name': '17_12000_2000.tif'
        },
        {
            'start_num': 1281,
            'end_num': 1410,
            'tif_name': '8_14000_0.tif'
        },
        {
            'start_num': 1411,
            'end_num': 1500,
            'tif_name': '7_12000_0.tif'
        },
        {
            'start_num': 1501,
            'end_num': 1600,
            'tif_name': '6_10000_0.tif'
        },
        {
            'start_num': 1601,
            'end_num': 1680,
            'tif_name': '5_8000_0.tif'
        },
        {
            'start_num': 1681,
            'end_num': 1770,
            'tif_name': '4_6000_0.tif'
        },
        {
            'start_num': 1771,
            'end_num': 1870,
            'tif_name': '3_4000_0.tif'
        },
        {
            'start_num': 1871,
            'end_num': 1952,
            'tif_name': '2_2000_0.tif'
        }

        # 添加更多的映射关系
    ]
    mappings_0199 = [
        {
            'start_num': 0,
            'end_num': 400,
            'tif_name': '2_2000_0.tif'
        },
        {
            'start_num': 401,
            'end_num': 650,
            'tif_name': '12_2000_2000.tif'
        },
        {
            'start_num': 651,
            'end_num': 800,
            'tif_name': '22_2000_4000.tif'
        },
        {
            'start_num': 801,
            'end_num': 950,
            'tif_name': '23_4000_4000.tif'
        },
        {
            'start_num': 951,
            'end_num': 1050,
            'tif_name': '24_6000_4000.tif'
        },
        {
            'start_num': 1051,
            'end_num': 1200,
            'tif_name': '25_8000_4000.tif'
        },
        {
            'start_num': 1201,
            'end_num': 1320,
            'tif_name': '26_10000_4000.tif'
        },
        {
            'start_num': 1321,
            'end_num': 1560,
            'tif_name': '27_12000_4000.tif'
        },
        {
            'start_num': 1561,
            'end_num': 1650,
            'tif_name': '17_12000_2000.tif'
        },
        {
            'start_num': 1651,
            'end_num': 1850,
            'tif_name': '7_12000_0.tif'
        },
        {
            'start_num': 1851,
            'end_num': 1950,
            'tif_name': '6_10000_0.tif'
        },
        {
            'start_num': 1951,
            'end_num': 2000,
            'tif_name': '5_8000_0.tif'
        },
        {
            'start_num': 2001,
            'end_num': 2100,
            'tif_name': '4_6000_0.tif'
        },
        {
            'start_num': 2101,
            'end_num': 2200,
            'tif_name': '3_4000_0.tif'
        },
        {
            'start_num': 2201,
            'end_num': 2254,
            'tif_name': '2_2000_0.tif'
        }
    ]


    create_pairs(uav_directory, tif_directory, pairs_txt_path, mappings_0103_2)

