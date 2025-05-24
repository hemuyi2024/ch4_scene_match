from osgeo import gdal
import numpy as np
def get_elevation_from_dsm(dsm_path, utm_x, utm_y):
    dataset = gdal.Open(dsm_path)
    if not dataset:
        raise FileNotFoundError(f"无法打开DSM文件: {dsm_path}")

    geotransform = dataset.GetGeoTransform()
    band = dataset.GetRasterBand(1)
    array = band.ReadAsArray()
    rows, cols = array.shape

    # === 手动进行 UTM → 像素坐标转换（适用于标准仿射矩阵） ===
    origin_x = geotransform[0]
    origin_y = geotransform[3]
    pixel_width = geotransform[1]
    pixel_height = geotransform[5]

    pixel_x = int(round((utm_x - origin_x) / pixel_width))
    pixel_y = int(round((utm_y - origin_y) / pixel_height))

    # 判断是否越界
    if 0 <= pixel_x < cols and 0 <= pixel_y < rows:
        elevation = array[pixel_y, pixel_x]  # 注意 y 是行，x 是列
        return elevation
    else:
        return None


def get_utm_3d_points_from_dsm(dsm_path, pts2_inliers_geo_utm):
    """
    根据输入的 UTM 坐标点，从 DSM 中提取高程，输出 3D 点。

    参数:
        dsm_path: str, DSM 文件路径
        pts2_inliers_geo_utm: (N, 2) numpy 数组，包含 UTM 坐标 (x, y)

    返回:
        satellite_3d_utm: (N, 3) numpy 数组，每行是 [x, y, elevation]
    """
    dataset = gdal.Open(dsm_path)
    if dataset is None:
        raise FileNotFoundError(f"无法打开 DSM 文件：{dsm_path}")

    # 获取仿射变换和影像数据
    geotransform = dataset.GetGeoTransform()
    band = dataset.GetRasterBand(1)
    dsm_array = band.ReadAsArray()
    rows, cols = dsm_array.shape

    # 提取仿射变换参数
    origin_x, pixel_width, _, origin_y, _, pixel_height = geotransform

    # 初始化输出数组
    satellite_3d_utm = np.zeros((len(pts2_inliers_geo_utm), 3))
    invalid_indices = []

    for idx, (utm_x, utm_y) in enumerate(pts2_inliers_geo_utm):
        pixel_x = int(round((utm_x - origin_x) / pixel_width))
        pixel_y = int(round((utm_y - origin_y) / pixel_height))
        print(f"zuobiao:{pixel_x},{pixel_y}")

        if 0 <= pixel_x < cols and 0 <= pixel_y < rows:
            elevation = dsm_array[pixel_y, pixel_x]
        else:
            elevation = -9999  # 或者使用 np.nan

        satellite_3d_utm[idx] = [utm_x, utm_y, elevation]

    return satellite_3d_utm