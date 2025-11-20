import os
import re

from torch.utils.hipify.hipify_python import mapping

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
                        uav_img_path = os.path.join("seu_uav_011006/",uav_img)
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
    uav_directory = "/home/lty/datasets_my/DJI/m300/seu_uav_011006"
    # TIF 影像文件夹路径
    tif_directory = "/home/lty/datasets_my/DJI/m300/seu_tif_m300"
    # 输出的 pairs.txt 文件路径
    pairs_txt_path = "/home/lty/outputs/scene_match_seu_0110_6/pairs.txt"

    # 指定编号范围映射关系 11-21-dji0200
    mappings_052405 = [
        {
            'start_num': 0,
            'end_num': 60,
            'tif_name': '31_3000_6000.tif'
        },
        {
            'start_num': 61,
            'end_num': 98,
            'tif_name': '32_4500_6000.tif'
        },
        {
            'start_num': 99,
            'end_num': 116,
            'tif_name': '33_6000_6000.tif'
        },
        {
            'start_num': 117,
            'end_num': 170,
            'tif_name': '26_6000_4500.tif'
        },
        {
            'start_num': 171,
            'end_num': 190,
            'tif_name': '20_7500_3000.tif'
        },
        {
            'start_num': 191,
            'end_num': 230,
            'tif_name': '12_6000_1500.tif'
        },
        {
            'start_num': 231,
            'end_num': 280,
            'tif_name': '5_6000_0.tif'
        },
        {
            'start_num': 281,
            'end_num': 310,
            'tif_name': '4_4500_0.tif'
        },
        {
            'start_num': 311,
            'end_num': 330,
            'tif_name': '3_3000_0.tif'
        },
        {
            'start_num': 331,
            'end_num': 359,
            'tif_name': '2_1500_0.tif'
        },
        {
            'start_num': 360,
            'end_num': 418,
            'tif_name': '8_0_1500.tif'
        },
        {
            'start_num': 419,
            'end_num': 465,
            'tif_name': '15_0_3000.tif'
        },
        {
            'start_num': 466,
            'end_num': 501,
            'tif_name': '22_0_4500.tif'
        },
    ]
    mappings_052411 = [
        {
            'start_num': 0,
            'end_num': 30,
            'tif_name': '8_0_1500.tif'
        },
        {
            'start_num': 31,
            'end_num': 80,
            'tif_name': '15_0_3000.tif'
        },
        {
            'start_num': 81,
            'end_num': 140,
            'tif_name': '22_0_4500.tif'
        },
        {
            'start_num': 141,
            'end_num': 190,
            'tif_name': '29_0_6000.tif'
        },
        {
            'start_num': 191,
            'end_num': 230,
            'tif_name': '30_1500_6000.tif'
        },
        {
            'start_num': 231,
            'end_num': 270,
            'tif_name': '31_3000_6000.tif'
        },
        {
            'start_num': 271,
            'end_num': 320,
            'tif_name': '32_4500_6000.tif'
        },
        {
            'start_num': 321,
            'end_num': 380,
            'tif_name': '25_4500_4500.tif'
        },
        {
            'start_num': 381,
            'end_num': 440,
            'tif_name': '18_4500_3000.tif'
        },
        {
            'start_num': 441,
            'end_num': 470,
            'tif_name': '11_4500_1500.tif'
        },
        {
            'start_num': 471,
            'end_num': 520,
            'tif_name': '5_6000_0.tif'
        },
        {
            'start_num': 521,
            'end_num': 600,
            'tif_name': '6_7500_0.tif'
        },
        {
            'start_num': 601,
            'end_num': 650,
            'tif_name': '13_7500_1500.tif'
        },
        {
            'start_num': 651,
            'end_num': 690,
            'tif_name': '20_7500_3000.tif'
        },
        {
            'start_num': 691,
            'end_num': 710,
            'tif_name': '27_7500_4500.tif'
        },
        {
            'start_num': 711,
            'end_num': 732,
            'tif_name': '33_6000_6000.tif'
        },
    ]
    mappings_052410 = [
        {
            'start_num': 0,
            'end_num': 90,
            'tif_name': '20_7500_3000.tif'
        },
        {
            'start_num': 91,
            'end_num': 154,
            'tif_name': '13_7500_1500.tif'
        },
        {
            'start_num': 155,
            'end_num': 200,
            'tif_name': '12_6000_1500.tif'
        },
        {
            'start_num': 201,
            'end_num': 240,
            'tif_name': '11_4500_1500.tif'
        },
        {
            'start_num': 241,
            'end_num': 286,
            'tif_name': '18_4500_3000.tif'
        },
        {
            'start_num': 287,
            'end_num': 325,
            'tif_name': '25_4500_4500.tif'
        },
        {
            'start_num': 326,
            'end_num': 370,
            'tif_name': '31_3000_6000.tif'
        },
        {
            'start_num': 371,
            'end_num': 425,
            'tif_name': '29_0_6000.tif'
        },
        {
            'start_num': 426,
            'end_num': 520,
            'tif_name': '22_0_4500.tif'
        },
        {
            'start_num': 521,
            'end_num': 606,
            'tif_name': '15_0_3000.tif'
        },


    ]
    mappings_052409 = [
        {
            'start_num': 0,
            'end_num': 75,
            'tif_name': '29_0_6000.tif'
        },
        {
            'start_num': 76,
            'end_num': 142,
            'tif_name': '31_3000_6000.tif'
        },
        {
            'start_num': 143,
            'end_num': 167,
            'tif_name': '32_4500_6000.tif'
        },
        {
            'start_num': 168,
            'end_num': 194,
            'tif_name': '25_4500_4500.tif'
        },
        {
            'start_num': 195,
            'end_num': 229,
            'tif_name': '18_4500_3000.tif'
        },
        {
            'start_num': 230,
            'end_num': 306,
            'tif_name': '11_4500_1500.tif'
        },
        {
            'start_num': 307,
            'end_num': 346,
            'tif_name': '12_6000_1500.tif'
        },
        {
            'start_num': 347,
            'end_num': 386,
            'tif_name': '5_6000_0.tif'
        },
        {
            'start_num': 387,
            'end_num': 424,
            'tif_name': '6_7500_0.tif'
        },
        {
            'start_num': 425,
            'end_num': 457,
            'tif_name': '13_7500_1500.tif'
        },
        {
            'start_num': 458,
            'end_num': 483,
            'tif_name': '20_7500_3000.tif'
        },
        {
            'start_num': 484,
            'end_num': 525,
            'tif_name': '21_9000_3000.tif'
        },
        {
            'start_num': 526,
            'end_num': 552,
            'tif_name': '27_7500_4500.tif'
        },
    ]
    mappings_city1 = [
        {
            'start_num': 1,
            'end_num': 10,
            'tif_name': '278_1906_2356.tif'
        },
        {
            'start_num': 11,
            'end_num': 19,
            'tif_name': '277_1756_2356.tif'
        },
        {
            'start_num': 20,
            'end_num': 27,
            'tif_name': '276_1606_2356.tif'
        },
        {
            'start_num': 28,
            'end_num': 36,
            'tif_name': '274_1306_2356.tif'
        },
        {
            'start_num': 37,
            'end_num': 49,
            'tif_name': '273_1156_2356.tif'
        },
        {
            'start_num': 50,
            'end_num': 59,
            'tif_name': '272_1006_2356.tif'
        },
        {
            'start_num': 60,
            'end_num': 69,
            'tif_name': '271_856_2356.tif'
        },
        {
            'start_num': 70,
            'end_num': 82,
            'tif_name': '270_706_2356.tif'
        },
        {
            'start_num': 83,
            'end_num': 90,
            'tif_name': '251_706_2206.tif'
        },
        {
            'start_num': 91,
            'end_num': 95,
            'tif_name': '250_556_2206.tif'
        },
        {
            'start_num': 96,
            'end_num': 100,
            'tif_name': '231_556_2056.tif'
        },
        {
            'start_num': 101,
            'end_num': 109,
            'tif_name': '212_556_1906.tif'
        },
        {
            'start_num': 110,
            'end_num': 122,
            'tif_name': '193_556_1756.tif'
        },
        {
            'start_num': 123,
            'end_num': 133,
            'tif_name': '174_556_1606.tif'
        },
        {
            'start_num': 134,
            'end_num': 145,
            'tif_name': '136_556_1306.tif'
        },
        {
            'start_num': 146,
            'end_num': 154,
            'tif_name': '117_556_1156.tif'
        },
        {
            'start_num': 155,
            'end_num': 164,
            'tif_name': '98_556_1006.tif'
        },
        {
            'start_num': 165,
            'end_num': 176,
            'tif_name': '79_556_856.tif'
        },
        {
            'start_num': 177,
            'end_num': 186,
            'tif_name': '60_556_706.tif'
        },
        {
            'start_num': 187,
            'end_num': 199,
            'tif_name': '42_706_556.tif'
        },
        {
            'start_num': 200,
            'end_num': 211,
            'tif_name': '43_856_556.tif'
        },
        {
            'start_num': 212,
            'end_num': 224,
            'tif_name': '25_1006_406.tif'
        },
        {
            'start_num': 225,
            'end_num': 236,
            'tif_name': '26_1156_406.tif'
        },
        {
            'start_num': 237,
            'end_num': 245,
            'tif_name': '27_1306_406.tif'
        },
        {
            'start_num': 246,
            'end_num': 258,
            'tif_name': '47_1456_556.tif'
        },
        {
            'start_num': 259,
            'end_num': 271,
            'tif_name': '67_1606_706.tif'
        },
        {
            'start_num': 272,
            'end_num': 290,
            'tif_name': '86_1606_856.tif'
        },
        {
            'start_num': 291,
            'end_num': 301,
            'tif_name': '104_1456_1006.tif'
        },
        {
            'start_num': 302,
            'end_num': 310,
            'tif_name': '123_1456_1156.tif'
        },
        {
            'start_num': 311,
            'end_num': 318,
            'tif_name': '141_1306_1306.tif'
        },
        {
            'start_num': 319,
            'end_num': 329,
            'tif_name': '160_1306_1456.tif'
        },
        {
            'start_num': 330,
            'end_num': 339,
            'tif_name': '180_1456_1606.tif'
        },
        {
            'start_num': 340,
            'end_num': 349,
            'tif_name': '181_1606_1606.tif'
        },
        {
            'start_num': 350,
            'end_num': 359,
            'tif_name': '183_1906_1606.tif'
        },
        {
            'start_num': 360,
            'end_num': 370,
            'tif_name': '184_2056_1606.tif'
        },
        {
            'start_num': 371,
            'end_num': 381,
            'tif_name': '185_2206_1606.tif'
        },
        {
            'start_num': 382,
            'end_num': 396,
            'tif_name': '205_2356_1756.tif'
        },
        {
            'start_num': 397,
            'end_num': 405,
            'tif_name': '224_2356_1906.tif'
        },
        {
            'start_num': 406,
            'end_num': 413,
            'tif_name': '243_2356_2056.tif'
        },
        {
            'start_num': 414,
            'end_num': 424,
            'tif_name': '261_2206_2206.tif'
        },
        {
            'start_num': 425,
            'end_num': 429,
            'tif_name': '280_2206_2356.tif'
        },

    ]
    mappings_city3 = [
        {
            'start_num': 1,
            'end_num': 10,
            'tif_name': '179_556_1906.tif'
        },
        {
            'start_num': 11,
            'end_num': 20,
            'tif_name': '163_556_1756.tif'
        },
        {
            'start_num': 21,
            'end_num': 28,
            'tif_name': '146_406_1606.tif'
        },
        {
            'start_num': 29,
            'end_num': 37,
            'tif_name': '130_406_1456.tif'
        },
        {
            'start_num': 38,
            'end_num': 45,
            'tif_name': '114_406_1306.tif'
        },
        {
            'start_num': 46,
            'end_num': 55,
            'tif_name': '98_406_1156.tif'
        },
        {
            'start_num': 56,
            'end_num': 65,
            'tif_name': '82_406_1006.tif'
        },
        {
            'start_num': 66,
            'end_num': 75,
            'tif_name': '66_406_856.tif'
        },
        {
            'start_num': 76,
            'end_num': 83,
            'tif_name': '50_406_706.tif'
        },
        {
            'start_num': 84,
            'end_num': 92,
            'tif_name': '34_406_556.tif'
        },
        {
            'start_num': 93,
            'end_num': 99,
            'tif_name': '18_406_406.tif'
        },
        {
            'start_num': 100,
            'end_num': 106,
            'tif_name': '19_556_406.tif'
        },
        {
            'start_num': 107,
            'end_num': 114,
            'tif_name': '20_706_406.tif'
        },
        {
            'start_num': 115,
            'end_num': 123,
            'tif_name': '21_856_406.tif'
        },
        {
            'start_num': 124,
            'end_num': 131,
            'tif_name': '22_1006_406.tif'
        },
        {
            'start_num': 132,
            'end_num': 142,
            'tif_name': '23_1156_406.tif'
        },
        {
            'start_num': 143,
            'end_num': 154,
            'tif_name': '24_1306_406.tif'
        },
        {
            'start_num': 155,
            'end_num': 162,
            'tif_name': '41_1456_556.tif'
        },
        {
            'start_num': 163,
            'end_num': 169,
            'tif_name': '42_1606_556.tif'
        },
        {
            'start_num': 170,
            'end_num': 178,
            'tif_name': '43_1756_556.tif'
        },
        {
            'start_num': 179,
            'end_num': 191,
            'tif_name': '60_1906_706.tif'
        },
        {
            'start_num': 192,
            'end_num': 199,
            'tif_name': '76_1906_856.tif'
        },
        {
            'start_num': 200,
            'end_num': 210,
            'tif_name': '92_1906_1006.tif'
        },
        {
            'start_num': 211,
            'end_num': 220,
            'tif_name': '108_1906_1156.tif'
        },
        {
            'start_num': 221,
            'end_num': 227,
            'tif_name': '123_1756_1306.tif'
        },
        {
            'start_num': 228,
            'end_num': 235,
            'tif_name': '122_1606_1306.tif'
        },
        {
            'start_num': 236,
            'end_num': 245,
            'tif_name': '121_1456_1306.tif'
        },
        {
            'start_num': 246,
            'end_num': 256,
            'tif_name': '120_1306_1306.tif'
        },
        {
            'start_num': 257,
            'end_num': 263,
            'tif_name': '119_1156_1306.tif'
        },
        {
            'start_num': 264,
            'end_num': 272,
            'tif_name': '118_1006_1306.tif'
        },
        {
            'start_num': 273,
            'end_num': 285,
            'tif_name': '135_1156_1456.tif'
        },
        {
            'start_num': 286,
            'end_num': 295,
            'tif_name': '152_1306_1606.tif'
        },
        {
            'start_num': 296,
            'end_num': 307,
            'tif_name': '169_1456_1756.tif'
        },
        {
            'start_num': 308,
            'end_num': 321,
            'tif_name': '185_1456_1906.tif'
        },
        {
            'start_num': 322,
            'end_num': 334,
            'tif_name': '184_1306_1906.tif'
        },
        {
            'start_num': 335,
            'end_num': 338,
            'tif_name': '199_1156_2056.tif'
        },
        {
            'start_num': 339,
            'end_num': 342,
            'tif_name': '198_1006_2056.tif'
        },
        {
            'start_num': 343,
            'end_num': 352,
            'tif_name': '197_856_2056.tif'
        },
        {
            'start_num': 353,
            'end_num': 362,
            'tif_name': '196_706_2056.tif'
        },
    ]
    mappings_city2 = [
        {
            'start_num': 1,
            'end_num': 22,
            'tif_name': '131_856_1606.tif'
        },
        {
            'start_num': 23,
            'end_num': 30,
            'tif_name': '117_856_1456.tif'
        },
        {
            'start_num': 31,
            'end_num': 36,
            'tif_name': '103_856_1306.tif'
        },
        {
            'start_num': 37,
            'end_num': 48,
            'tif_name': '89_856_1156.tif'
        },
        {
            'start_num': 49,
            'end_num': 63,
            'tif_name': '75_856_1006.tif'
        },
        {
            'start_num': 64,
            'end_num': 73,
            'tif_name': '61_856_856.tif'
        },
        {
            'start_num': 74,
            'end_num': 88,
            'tif_name': '47_856_706.tif'
        },
        {
            'start_num': 89,
            'end_num': 94,
            'tif_name': '33_856_556.tif'
        },
        {
            'start_num': 95,
            'end_num': 100,
            'tif_name': '34_1006_556.tif'
        },
        {
            'start_num': 101,
            'end_num': 110,
            'tif_name': '35_1156_556.tif'
        },
        {
            'start_num': 111,
            'end_num': 123,
            'tif_name': '36_1306_556.tif'
        },
        {
            'start_num': 124,
            'end_num': 132,
            'tif_name': '37_1456_556.tif'
        },
        {
            'start_num': 133,
            'end_num': 140,
            'tif_name': '38_1606_556.tif'
        },
        {
            'start_num': 141,
            'end_num': 148,
            'tif_name': '39_1756_556.tif'
        },
        {
            'start_num': 149,
            'end_num': 161,
            'tif_name': '53_1756_706.tif'
        },
        {
            'start_num': 162,
            'end_num': 175,
            'tif_name': '67_1756_856.tif'
        },
        {
            'start_num': 176,
            'end_num': 182,
            'tif_name': '66_1606_856.tif'
        },
        {
            'start_num': 183,
            'end_num': 193,
            'tif_name': '65_1456_856.tif'
        },
        {
            'start_num': 194,
            'end_num': 204,
            'tif_name': '64_1306_856.tif'
        },
        {
            'start_num': 205,
            'end_num': 217,
            'tif_name': '78_1306_1006.tif'
        },
        {
            'start_num': 218,
            'end_num': 228,
            'tif_name': '106_1306_1306.tif'
        },
        {
            'start_num': 229,
            'end_num': 239,
            'tif_name': '107_1456_1306.tif'
        },
        {
            'start_num': 240,
            'end_num': 250,
            'tif_name': '108_1606_1306.tif'
        },
        {
            'start_num': 251,
            'end_num': 261,
            'tif_name': '109_1756_1306.tif'
        },
        {
            'start_num': 262,
            'end_num': 272,
            'tif_name': '123_1756_1456.tif'
        },
        {
            'start_num': 273,
            'end_num': 293,
            'tif_name': '136_1606_1606.tif'
        },
        {
            'start_num': 294,
            'end_num': 304,
            'tif_name': '149_1456_1756.tif'
        },
        {
            'start_num': 305,
            'end_num': 318,
            'tif_name': '134_1306_1606.tif'
        },
        {
            'start_num': 319,
            'end_num': 328,
            'tif_name': '119_1156_1456.tif'
        },

    ]
    mappings_0110_6 = [
        {
            'start_num': 0,
            'end_num': 50,
            'tif_name': '1_0_0.tif'
        },
        {
            'start_num': 51,
            'end_num': 100,
            'tif_name': '8_0_1500.tif'
        },
        {
            'start_num': 101,
            'end_num': 137,
            'tif_name': '15_0_3000.tif'
        },
        {
            'start_num': 138,
            'end_num': 190,
            'tif_name': '22_0_4500.tif'
        },
        {
            'start_num': 191,
            'end_num': 237,
            'tif_name': '23_1500_4500.tif'
        },
        {
            'start_num': 238,
            'end_num': 265,
            'tif_name': '24_3000_4500.tif'
        },
        {
            'start_num': 266,
            'end_num': 303,
            'tif_name': '25_4500_4500.tif'
        },
        {
            'start_num': 304,
            'end_num': 345,
            'tif_name': '26_6000_4500.tif'
        },
        {
            'start_num': 346,
            'end_num': 390,
            'tif_name': '27_7500_4500.tif'
        },
        {
            'start_num': 391,
            'end_num': 423,
            'tif_name': '20_7500_3000.tif'
        },
        {
            'start_num': 424,
            'end_num': 463,
            'tif_name': '13_7500_1500.tif'
        },
        {
            'start_num': 464,
            'end_num': 507,
            'tif_name': '6_7500_0.tif'
        },
        {
            'start_num': 508,
            'end_num': 548,
            'tif_name': '5_6000_0.tif'
        },
        {
            'start_num': 549,
            'end_num': 582,
            'tif_name': '4_4500_0.tif'
        },
        {
            'start_num': 583,
            'end_num': 615,
            'tif_name': '3_3000_0.tif'
        },
        {
            'start_num': 616,
            'end_num': 680,
            'tif_name': '2_1500_0.tif'
        },
        {
            'start_num': 681,
            'end_num': 724,
            'tif_name': '1_0_0.tif'
        },
    ]
    mappings_0110_11 = [
        {
            'start_num': 0,
            'end_num': 250,
            'tif_name': '25_4500_4500.tif'
        },
        {
            'start_num': 251,
            'end_num': 390,
            'tif_name': '18_4500_3000.tif'
        },
        {
            'start_num': 391,
            'end_num': 550,
            'tif_name': '11_4500_1500.tif'
        },
        {
            'start_num': 551,
            'end_num': 670,
            'tif_name': '3_3000_0.tif'
        },
        {
            'start_num': 671,
            'end_num': 850,
            'tif_name': '2_1500_0.tif'
        },
        {
            'start_num': 851,
            'end_num': 990,
            'tif_name': '8_0_1500.tif'
        },
        {
            'start_num': 991,
            'end_num': 1060,
            'tif_name': '15_0_3000.tif'
        },
        {
            'start_num': 1061,
            'end_num': 1170,
            'tif_name': '22_0_4500.tif'
        },
        {
            'start_num': 1171,
            'end_num': 1260,
            'tif_name': '23_1500_4500.tif'
        },
        {
            'start_num': 1261,
            'end_num': 1350,
            'tif_name': '24_3000_4500.tif'
        },
        {
            'start_num': 1351,
            'end_num': 1427,
            'tif_name': '25_4500_4500.tif'
        },
    ]
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


    create_pairs(uav_directory, tif_directory, pairs_txt_path, mappings_0110_6)

