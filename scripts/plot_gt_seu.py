from osgeo import osr
import cv2

# from scripts.tum2geo import output_file

gt_file = "/home/lty/outputs/seu0524/005/gt.txt"
geotransform_file = "/home/lty/scripts/seu_geotransform_fix.txt"
map_file = "/home/lty/data/SEU/seu_resized/seu_resized_m300.tif"
output_file = "/home/lty/outputs/seu0524/005/gt.png"

def plot_gt(gt_file=gt_file, geotransform_file=geotransform_file, source_epsg=4326, target_epsg=32650,
            map_file=map_file):
    scale = 0.2
    geotransform = []
    with open(geotransform_file, "r") as f:
        # 逐行读取文件内容
        for line in f:
            # 去除行首尾的空白字符和换行符
            line = line.strip()
            if line:
                try:
                    # 将字符串转换为浮点数
                    value = float(line)
                    # 将数值添加到列表中
                    geotransform.append(value)
                except ValueError:
                    print(f"无法将以下内容转换为数值：'{line}'")
                    # 根据需要，可以选择跳过或停止程序
                    continue
    # 输出读取到的 geotransform 数据
    print("Geotransform 数组：\n", geotransform)

    # 读取 GT 数据
    gt_data = []
    with open(gt_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # 假设格式为: 118.7865, 32.0591, 15
            parts = line.split(",")
            if len(parts) == 2:
                lon_str, lat_str = parts
                lon = float(lon_str.strip())
                lat = float(lat_str.strip())
                gt_data.append((lon, lat))
                # print(f"添加坐标 ({lon}, {lat})")



    # 至此，gt_data 中将只包含 (lon, lat) 的元组列表，例如：
    # [(118.7865, 32.0591), (118.7865, 32.0591), ...]
    source_srs = osr.SpatialReference()
    source_srs.ImportFromEPSG(source_epsg)

    target_srs = osr.SpatialReference()
    target_srs.ImportFromEPSG(target_epsg)

    coord_transform = osr.CoordinateTransformation(source_srs, target_srs)
    # 将地理坐标转换为投影坐标
    gt_traj = []
    for lon, lat in gt_data:
        x, y, _ = coord_transform.TransformPoint(lat, lon)
        print(f"投影坐标 ({x}, {y})")
        x_in_map = ((x - geotransform[0]) / geotransform[1])*scale
        y_in_map = -((geotransform[3]- y ) / geotransform[5])*scale
        print(f"地图坐标 ({x_in_map}, {y_in_map})")
        gt_traj.append((x_in_map, y_in_map))
    gt_traj = [(int(x), int(y)) for x, y in gt_traj]
    print("size of gt_traj: ", len(gt_traj))
    map_image = cv2.imread(map_file)
    for i in range(len(gt_traj)):
        cv2.circle(map_image, gt_traj[i], radius=1, color=(0, 255, 0), thickness=1)  # 绿色点
        # 如果不是第一个点，绘制关键帧之间的连线
        if i > 0:
            cv2.line(map_image, gt_traj[i - 1], gt_traj[i], color=(0, 255, 0), thickness=6)  # 蓝色线
            print(f"绘制连线：{gt_traj[i - 1]} -> {gt_traj[i]}")
    cv2.imwrite(output_file, map_image)


if __name__ == '__main__':
    plot_gt()