import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from pathlib import Path
import h5py

from hloc.visualization import plot_images, plot_keypoints
from hloc.utils.io import read_image


def get_keypoints(path: Path, name: str, return_scores=False, return_uncertainty=False):
    with h5py.File(str(path), "r", libver="latest") as hfile:
        group = hfile[name]
        kpts = group["keypoints"][()]

        scores = group["scores"][()] if return_scores and "scores" in group else None
        uncertainty = group["keypoints"].attrs.get("uncertainty") if return_uncertainty else None

    if return_scores and return_uncertainty:
        return kpts, scores, uncertainty
    elif return_scores:
        return kpts, scores
    elif return_uncertainty:
        return kpts, uncertainty
    return kpts

def draw_keypoints_colored(
    image_dir: Path,
    image_names: list[str],
    feature_path: Path,
    color_by: str = "score",  # 可选："score" / "uncertainty" / "none"
    ps: float = 2.0,
):
    # 读取图像
    images = [read_image(image_dir / name) for name in image_names]
    plot_images(images)

    # 读取关键点 + 值
    keypoints_list, color_values = [], []
    for name in image_names:
        if color_by == "score":
            kpts, scores = get_keypoints(feature_path, name, return_scores=True)
            color_values.append(scores)
        elif color_by == "uncertainty":
            kpts, uncertainty = get_keypoints(feature_path, name, return_uncertainty=True)
            if isinstance(uncertainty, np.ndarray):
                color_values.append(uncertainty)
            else:
                print(f"[警告] 图像 {name} 的 uncertainty 不是数组，跳过颜色编码")
                color_values.append(None)
        else:
            kpts = get_keypoints(feature_path, name)
            color_values.append(None)
        keypoints_list.append(kpts)

    # 做归一化 + colormap
    colors_list = []
    if all(v is not None for v in color_values):
        flat_vals = np.concatenate(color_values)
        norm = mcolors.Normalize(vmin=flat_vals.min(), vmax=flat_vals.max())
        cmap = cm.get_cmap("plasma")

        for vals in color_values:
            colors = [cmap(norm(v)) for v in vals]
            colors_list.append(colors)
    else:
        colors_list = ["lime"] * len(keypoints_list)

    # 绘制
    plot_keypoints(keypoints_list, colors=colors_list, ps=ps)
    plt.show()

if __name__ == '__main__':
    image_dir = Path("/home/lty/test/match_playground/")
    img_1 = "seu_uav/001.jpg"
    img_2 = "seu_tif/2462_1112.jpg"
    features_1_path = Path("../output_test/features_1.h5")

    draw_keypoints_colored(
        image_dir=image_dir,
        image_names=[img_1, img_2],
        feature_path=features_1_path,
        color_by="score",  # 可选：score / uncertainty / none
        ps=2,
    )
