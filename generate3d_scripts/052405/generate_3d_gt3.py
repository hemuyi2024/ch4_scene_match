import numpy as np

input_file = "/home/lty/paper/results/052409/traj0603(3d)/gt(3d).txt"
output_file = "/home/lty/paper/results/052409/traj0603(3d)/gt(3d)_minus8.txt"

# 读取数据
data = np.loadtxt(input_file)

# 第三列（Z）减 8
data[:, 2] = data[:, 2] - 8

# 保存结果
np.savetxt(output_file, data, fmt="%.9f")

print(f"已处理完成，保存到：{output_file}")
