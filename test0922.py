

import h5py

path = "/home/lty/outputs/RealUAV/city1/netvlad/db/global-feats-netvlad.h5"
with h5py.File(path, "r") as f:
    # 遍历所有数据集
    def print_name(name, obj):
        if isinstance(obj, h5py.Dataset):
            print(f"{name} -> shape={obj.shape}, dtype={obj.dtype}")

    f.visititems(print_name)

