import csv
import os

import numpy as np

import data_projection
import data_struct


alpha = 0.0  # 1.0模型 0.0积分
omega = 1  # trick 模型速率偏慢，指定单次预测速度乘一个值，可以提升模型效果，记录的时候也可以记录下来
gamma = 1

model_pose = False

data_dir = "data_gps/2024-09-30 09-38-09.csv"
proj_dir = "proj_info/2024-09-30 09-39-05.csv"

# 指定输出文件夹地址
data_out_dir = os.path.join(os.path.dirname(__file__), 'test')
os.makedirs(data_out_dir, exist_ok=True)  # Ensure the directory exists

def infer_bearing(prj_sen_units, crnt_brng, drift=0, collect_hz=50):
    gy_zs = [u.senz * 180.0 / np.pi - drift for u in prj_sen_units]
    bearing_diff = sum(gy_zs) / len(gy_zs) * -1.0
    return (crnt_brng + bearing_diff) % 360.0

def read_from_file(path):
    gyr_units = []
    with open(path, 'r') as fd:
        next(fd)  # 跳过第一行
        for line in fd:
            try:
                gyr_unit = data_struct.GyroUnit(line)
                gyr_units.append(gyr_unit)
            except AssertionError:
                continue
    return gyr_units


# 定义打印格式化结果的函数
def print_formatted(X, Y, Z):
    for i, x in enumerate(X):
        print(f"X[{i}] = {x};")
    for i, y in enumerate(Y):
        print(f"Y[{i}] = {y};")
    for i, z in enumerate(Z):
        print(f"Z[{i}] = {z};")


path = data_dir
csv_file_name = f"test_out"
csv_file_path = os.path.join(data_out_dir, csv_file_name)

print('load %s ...' % path)
gyr_units = read_from_file(path)

with open(proj_dir, 'r') as file:
    # 读取文件中的数据
    data = file.read().strip().split(',')

    # 将数据转为 float 类型并分别赋值
    X = [float(data[0]), float(data[1]), float(data[2])]
    Y = [float(data[3]), float(data[4]), float(data[5])]
    Z = [float(data[6]), float(data[7]), float(data[8])]

    print_formatted(X, Y, Z)

i = 0
j = 0
k = 0

#####################################
# 在这里修改为文件里的需要补偿的时间戳
timestamp = gyr_units[0].timestamp

gyr_one_step_units = []

# 单条轨迹记录时间
start_time = 0

condition = True

seg_init_brng = 270

with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)

    while condition:
        # 那么此时应该先row
        row = [
            str(seg_init_brng),
            str(timestamp),
        ]
        writer.writerow(row)

        print(row)

        while j < len(gyr_units):
            if gyr_units[j].timestamp < timestamp + 1000:
                gyr_one_step_units.append(gyr_units[j])
                j += 1
            else:
                break
        start_time += 1

        timestamp += 1000

        # 单步预测
        prj_gyr_units = []
        for unit in gyr_one_step_units:
            prj_gyr_unit = data_projection.project_imu(unit, X, Y, Z)
            prj_gyr_units.append(prj_gyr_unit)

        seg_init_brng = infer_bearing(prj_gyr_units, seg_init_brng, collect_hz=50, drift=0)

        gyr_one_step_units = []

        if j == len(gyr_units):
            condition = False