import os
import re
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from math import radians, sin, cos, sqrt, atan2
import matplotlib.pyplot as plt

# 定义命名空间
namespaces = {
    'kml': 'http://www.opengis.net/kml/2.2',
    'gx': 'http://www.google.com/kml/ext/2.2',
    'atom': 'http://www.w3.org/2005/Atom'
}


# 读取文件夹下所有文件的第一行
def read_first_line_from_files(directory):
    first_lines = []
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'r') as file:
                first_line = file.readline().strip()
                first_lines.append((filename, first_line))
    return first_lines


# 比较时间戳，忽略毫秒部分
def compare_time(time1, time2):
    time_format = "%H:%M:%S"
    t1 = datetime.strptime(time1.split('.')[0], time_format)
    t2 = datetime.strptime(time2.split('.')[0], time_format)
    return t1 == t2

# 提取 KML 数据并转换时间戳为北京时间
def extract_kml_data(kml_file):
    tree = ET.parse(kml_file)
    root = tree.getroot()

    pattern_description = re.compile(
        r'UTC:\s*(\d{2}:\d{2}:\d{2})\.?\d*<br>.*?Speed\s*([\d.]+)\s*\[m/s\]\s*<br>Course\s*([\d.]+)\s*\[deg\]',
        re.DOTALL
    )

    kml_data = []

    # 遍历所有的 Placemark 元素
    for placemark in root.findall('.//kml:Placemark', namespaces):
        description = placemark.find('kml:description', namespaces)
        coordinates = placemark.find('.//kml:coordinates', namespaces)

        if description is not None and description.text is not None and coordinates is not None and coordinates.text is not None:
            description_text = description.text
            coordinates_text = coordinates.text.strip()

            match_description = pattern_description.search(description_text)
            if match_description:
                utc_time = match_description.group(1)
                speed = float(match_description.group(2))
                course = float(match_description.group(3))
                lon, lat, _ = map(float, coordinates_text.split(','))

                # 转换为北京时间
                utc_datetime = datetime.strptime(utc_time, "%H:%M:%S")
                bj_datetime = utc_datetime + timedelta(hours=8)  # 转换为北京时间
                bj_time = bj_datetime.strftime("%H:%M:%S")  # 格式化为字符串

                kml_data.append({
                    'time': bj_time,  # 保存为北京时间
                    'lat': lat,
                    'lon': lon,
                    'speed': speed,
                    'course': course
                })
    return kml_data


# 根据时间戳累积 Speed 到 150，并找到新的时间戳
def find_cumulative_speed_timestamp(kml_data, start_time):
    cumulative_speed = 0
    for data in kml_data:
        if compare_time(start_time, data['time']) or cumulative_speed > 0:
            cumulative_speed += data['speed']
            if cumulative_speed >= 150:
                return data['time']  # 返回新的时间戳
    return None


# 打印文件和 KML 数据
def print_data_between_timestamps(file_data, kml_data, start_time, end_time):
    print(f"Start Time: {start_time}, End Time: {end_time}")
    result = []

    # print("\nKML Data:")
    for data in kml_data:
        if compare_time_range(data['time'], start_time, end_time):
            # print(f"KML Data - Time: {data['time']}, Lat: {data['lat']}, Lon: {data['lon']}, Speed: {data['speed']}, Course: {data['course']}")
            result.append({
                'time': data['time'],
                'lat': data['lat'],
                'lon': data['lon'],
                'speed': data['speed'],
                'course': data['course']
            })
    return result

# 比较两个时间戳范围内的值，忽略毫秒部分
def compare_time_range(time, start, end):
    time_format = "%H:%M:%S"
    t = datetime.strptime(time.split('.')[0], time_format)  # 忽略毫秒部分
    t_start = datetime.strptime(start, time_format)
    t_end = datetime.strptime(end, time_format)
    return t_start <= t <= t_end

# 新的函数：读取文件中两个时间戳之间的数据
def read_file_between_timestamps(filename, start_time, end_time):
    result = []
    with open(filename, 'r') as file:
        lines = file.readlines()
        # print(f"\nData from file {filename} between {start_time} and {end_time}:")
        for line in lines:
            line_data = line.strip().split(',')
            file_time = line_data[0]  # 提取时间戳
            if compare_time_range(file_time, start_time, end_time):
                # 只提取前五列：时间、纬度、经度、速度、航向
                time = line_data[0]
                lon = float(line_data[1])
                lat = float(line_data[2])
                speed = float(line_data[3])
                course = float(line_data[4])

                # 格式化输出
                # print(f"Time: {time}, Lat: {lat:.6f}, Lon: {lon:.6f}, Speed: {speed:.2f}, Course: {course:.2f}")

                # 将数据存储到结果列表中
                result.append({
                    'time': time,
                    'lat': lat,
                    'lon': lon,
                    'speed': speed,
                    'course': course
                })
    return result


# 计算两点之间的距离（基于经纬度，单位：米）
def haversine(lon1, lat1, lon2, lat2):
    # 地球半径（单位：米）
    R = 6371000
    # 将角度转换为弧度
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Haversine 公式
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # 计算距离
    distance = R * c
    return distance


# 比较结果
def compare_kml_file_data(result_kml, result_file):
    if not result_kml or not result_file:
        print("KML或文件数据为空，无法比较。")
        return

    # 比较第一个值的速度和航向
    first_kml = result_kml[0]
    first_file = result_file[0]

    print("Comparing first values:")
    print(f"KML - Speed: {first_kml['speed']}, Course: {first_kml['course']}")
    print(f"File - Speed: {first_file['speed']}, Course: {first_file['course']}")

    speed_diff = abs(first_kml['speed'] - first_file['speed'])
    course_diff = abs(first_kml['course'] - first_file['course'])

    print(f"Speed difference: {speed_diff}")
    print(f"Course difference: {course_diff}")

    # 比较最后一个值的经纬度之间的距离
    last_kml = result_kml[-1]
    last_file = result_file[-1]

    distance = haversine(last_kml['lon'], last_kml['lat'], last_file['lon'], last_file['lat'])

    print("\nComparing last values:")
    print(f"KML - Lat: {last_kml['lat']}, Lon: {last_kml['lon']}")
    print(f"File - Lat: {last_file['lat']}, Lon: {last_file['lon']}")

    print(f"Distance between last KML and File points: {distance:.2f} meters")


# 提取速度和航向
def extract_speed_and_course(data):
    speed = [entry['speed'] for entry in data]
    course = [entry['course'] for entry in data]
    return speed, course


# 绘制图表
def plot_speed_and_course(result_kml, result_file):
    kml_speed, kml_course = extract_speed_and_course(result_kml)
    file_speed, file_course = extract_speed_and_course(result_file)

    num_points = len(kml_speed)

    if num_points != len(file_speed):
        print("KML 数据和文件数据的长度不一致，无法绘图。")
        return

    # 生成横坐标：1, 2, 3, ..., len(kml_speed)
    x_values = list(range(1, num_points + 1))

    # 绘制速度图
    plt.figure(figsize=(10, 5))

    # 子图 1: 速度对比
    plt.subplot(1, 2, 1)
    plt.plot(x_values, kml_speed, label='KML Speed', color='blue')
    plt.plot(x_values, file_speed, label='File Speed', color='orange')
    plt.title('Speed Comparison')
    plt.xlabel('Index')
    plt.ylabel('Speed (m/s)')
    plt.legend()

    # 子图 2: 航向对比
    plt.subplot(1, 2, 2)
    plt.plot(x_values, kml_course, label='KML Course', color='blue')
    plt.plot(x_values, file_course, label='File Course', color='orange')
    plt.title('Course Comparison')
    plt.xlabel('Index')
    plt.ylabel('Course (degrees)')
    plt.legend()

    # 调整布局，显示图像
    plt.tight_layout()
    plt.show()  # 显示图像

# 累加 result_file 中的 speed 值
def sum_file_speed(result_file):
    total_speed = sum([entry['speed'] for entry in result_file])
    print(f"Total Speed in result_file: {total_speed:.2f} m/s")
    return total_speed

# 主函数，找到时间戳并累计 Speed
def match_files_with_kml(directory, kml_file):
    first_lines = read_first_line_from_files(directory)
    kml_data = extract_kml_data(kml_file)

    for filename, first_line in first_lines:
        file_data = first_line.split(',')
        file_time = file_data[0]
        file_lat = float(file_data[1])
        file_lon = float(file_data[2])
        file_speed = float(file_data[3])
        file_course = float(file_data[4])

        # 与 KML 文件数据进行时间戳比较
        for data in kml_data:
            if compare_time(file_time, data['time']):
                # 找到起始时间戳后，累积速度并找到新的时间戳
                new_timestamp = find_cumulative_speed_timestamp(kml_data, data['time'])
                if new_timestamp:
                    # 打印两个时间戳之间的所有数据
                    print(f"File: {filename}")
                    # print(
                    #     f"File Data - Time: {file_time}, Lat: {file_lat}, Lon: {file_lon}, Speed: {file_speed}, Course: {file_course}")
                    result_kml = print_data_between_timestamps(first_lines, kml_data, data['time'], new_timestamp)

                    # 重新读取文件并打印两个时间戳之间的数据
                    result_file = read_file_between_timestamps(os.path.join(directory, filename), data['time'], new_timestamp)

                    # 调用累加函数
                    total_file_speed = sum_file_speed(result_file)

                    compare_kml_file_data(result_kml, result_file)

                    plot_speed_and_course(result_kml, result_file)

                    print("-" * 50)


# 示例使用
directory = 'test_data/22113-35170'  # 替换为文件所在目录路径
kml_file = 'kml/NMPL21420006K_2024-09-30_09-19-02.kml'  # 替换为KML文件路径

match_files_with_kml(directory, kml_file)

