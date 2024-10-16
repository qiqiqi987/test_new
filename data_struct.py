#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Time       : 2024/10/16 12:06
@Author     : suyufei
@File       : data_struct.py
@DevTool    : PyCharm
"""


class AccelUnit:
    def __init__(self, line):
        assert 'acc' in line
        _items = line.strip().split(',')
        # 这里通过判断字段数量来区分不同的数据格式
        if len(_items) == 6:
            # 旧的格式
            self.timestamp = int(float(_items[1])) // 1_000_000 # 第2个字段作为时间戳
            self.senx = float(_items[2])  # 第3个字段
            self.seny = float(_items[3])  # 第4个字段
            self.senz = float(_items[4])  # 第5个字段
            self.accuracy = float(_items[5])  # 第6个字段
        elif len(_items) == 7:
            # 新的格式
            self.timestamp = int(float(_items[1]))  # 第2个字段作为时间戳
            self.senx = float(_items[2])  # 第3个字段
            self.seny = float(_items[3])  # 第4个字段
            self.senz = float(_items[4])  # 第5个字段
            self.accuracy = float(_items[6])  # 第7个字段
        else:
            raise ValueError("Invalid data line format")

    @property
    def out_str(self):
        return 'acc,%d,%.6f,%.6f,%.6f,%.2f' \
            % (self.timestamp * 1_000_000, self.senx, self.seny, self.senz, self.accuracy)

    def __repr__(self):
        return 'acc,%d,%.4f,%.4f,%.4f,%.1f' \
            % (self.timestamp, self.senx, self.seny, self.senz, self.accuracy)


class LAccelUnit:
    def __init__(self, line):
        assert 'l_acc' in line
        _items = line.strip().split(',')
        # 这里通过判断字段数量来区分不同的数据格式
        if len(_items) == 6:
            # 旧的格式
            self.timestamp = int(float(_items[1])) // 1_000_000 # 第2个字段作为时间戳
            self.senx = float(_items[2])  # 第3个字段
            self.seny = float(_items[3])  # 第4个字段
            self.senz = float(_items[4])  # 第5个字段
            self.accuracy = float(_items[5])  # 第6个字段
        elif len(_items) == 7:
            # 新的格式
            self.timestamp = int(float(_items[1]))  # 第2个字段作为时间戳
            self.senx = float(_items[2])  # 第3个字段
            self.seny = float(_items[3])  # 第4个字段
            self.senz = float(_items[4])  # 第5个字段
            self.accuracy = float(_items[6])  # 第7个字段
        else:
            raise ValueError("Invalid data line format")

    @property
    def out_str(self):
        return 'l_acc,%d,%.6f,%.6f,%.6f,%.2f' \
            % (self.timestamp * 1_000_000, self.senx, self.seny, self.senz, self.accuracy)

    def __repr__(self):
        return 'l_acc,%d,%.4f,%.4f,%.4f,%.1f' \
            % (self.timestamp, self.senx, self.seny, self.senz, self.accuracy)


class GyroUnit:
    def __init__(self, line):
        _items = line.strip().split(',')
        # 这里通过判断字段数量来区分不同的数据格式
        if len(_items) == 6:
            # 旧的格式
            self.timestamp = int(float(_items[1])) // 1_000_000 # 第2个字段作为时间戳
            self.senx = float(_items[2])  # 第3个字段
            self.seny = float(_items[3])  # 第4个字段
            self.senz = float(_items[4])  # 第5个字段
            self.accuracy = float(_items[5])  # 第6个字段
        elif len(_items) == 7:
            # 新的格式
            self.timestamp = int(float(_items[1]))  # 第2个字段作为时间戳
            self.senx = float(_items[2])  # 第3个字段
            self.seny = float(_items[3])  # 第4个字段
            self.senz = float(_items[4])  # 第5个字段
            self.accuracy = float(_items[6])  # 第7个字段
        elif len(_items) == 16:
            # 初始格式
            self.timestamp = int(_items[0])
            self.senx = float(_items[7])
            self.seny = float(_items[8])
            self.senz = float(_items[9])
        else:
            raise ValueError("Invalid data line format")

    @property
    def out_str(self):
        return 'gyr,%d,%.6f,%.6f,%.6f,%.2f' \
            % (self.timestamp * 1_000_000, self.senx, self.seny, self.senz, self.accuracy)

    def __repr__(self):
        return 'gyro,%d,%.4f,%.4f,%.4f,%.1f' \
            % (self.timestamp, self.senx, self.seny, self.senz, self.accuracy)


# class GravityUnit:
#     def __init__(self, line):
#         assert line.startswith('gra')
#         _items = line.strip().split(',')
#         self.timestamp = int(float(_items[1])) // 1_000_000
#         self.senx = float(_items[2])
#         self.seny = float(_items[3])
#         self.senz = float(_items[4])
#         self.accuracy = float(_items[5])
#
#     @property
#     def out_str(self):
#         return 'gra,%d,%.6f,%.6f,%.6f,%.2f' \
#                % (self.timestamp * 1_000_000, self.senx, self.seny, self.senz, self.accuracy)
#
#     def __repr__(self):
#         return 'grv,%d,%.4f,%.4f,%.4f,%.1f' \
#                % (self.timestamp, self.senx, self.seny, self.senz, self.accuracy)


class GnssUnit:
    def __init__(self, line):
        assert line.startswith('gnss') or line.startswith('TYPE_GPS_SENSOR')

        # 替换 'null' 为 '0'
        if 'null' in line:
            line = line.replace('null', '0')

        # 拆分数据行
        _items = line.strip().split(',')

        if len(_items) == 10:
            # 旧格式
            self.timestamp = int(_items[1])
            self.lon = round(float(_items[2]), 6)
            self.lat = round(float(_items[3]), 6)
            self.accuracy = round(float(_items[4]), 2)
            self.spd = round(float(_items[5]), 2)
            self.spd_acc = round(float(_items[6]), 2)
            self.brng = round(float(_items[7]), 2)
            self.brng_acc = round(float(_items[8]), 2)
            self.gnss_time = int(_items[9])

        elif len(_items) == 16:
            # 新格式
            self.timestamp = int(_items[2])  # 第4个字段作为时间戳
            self.lon = round(float(_items[3]), 6)  # 第5个字段
            self.lat = round(float(_items[4]), 6)  # 第6个字段
            self.accuracy = round(float(_items[6]), 2)  # 第8个字段
            self.spd = round(float(_items[8]), 2)  # 第9个字段
            self.spd_acc = round(float(_items[15]), 2)  # 第14个字段
            self.brng = round(float(_items[7]), 2)  # 第10个字段
            self.brng_acc = round(float(_items[14]), 2)  # 第15个字段
            self.gnss_time = int(_items[10])  # 第11个字段

    @property
    def loc_str(self):
        return '%.6f,%.6f' % (self.lon, self.lat)

    @property
    def loc_wgs84_str(self):
        return self.loc_str

    @property
    def out_str(self):
        return 'gnss,%d,%.6f,%.6f,%.2f,%.2f,%.2f,%.2f,%.2f,%d' \
            % (self.timestamp, self.lon, self.lat, self.accuracy,
               self.spd, self.spd_acc, self.brng, self.brng_acc, self.gnss_time)

    def __repr__(self):
        return 'gnss,%d,%.6f,%.6f,%d' % (self.timestamp, self.lon, self.lat, self.gnss_time)


class Test12Unit:
    def __init__(self, line):
        assert line.startswith('acc') \
               or line.startswith('gyr') \
               or line.startswith('gnss')
        if line.startswith('acc'):
            self.obj = AccelUnit(line)
        elif line.startswith('gyr'):
            self.obj = GyroUnit(line)
        elif line.startswith('gnss'):
            self.obj = GnssUnit(line)
        else:
            self.obj = None

        if self.obj is not None:
            self.timestamp = self.obj.timestamp
        else:
            self.timestamp = None


class DDUnit(object):
    # 滴滴数据结构
    def __init__(self, line):
        _items = line.strip().split(',')

        if 'acc' in line:
            self.obj = AccelUnit(line)
        elif 'gyr' in line:
            self.obj = GyroUnit(line)
        elif 'gps' in line:
            self.obj = GnssUnit(line)
        else:
            self.obj = None

        if self.obj is not None:
            self.timestamp = self.obj.timestamp
        else:
            self.timestamp = None


class GDUnit(object):
    # 高德数据结构
    # ACC, 时间戳(ms), ax, ay, az
    # GYR, 时间戳(ms), gx, gy, gz
    # MGC, 时间戳(ms), mx, my, mz
    # GPS, 时间戳(ms), lon, lat, alt, radius, bearing, speed, utc_time
    def __init__(self, line) -> None:
        # assert isinstance(line, str)
        assert line.startswith('ACC') or line.startswith('GYR') or line.startswith('GPS')
        self.type = ''
        if line.startswith('GPS'):
            self.gps(line)
            self.type = 'GPS'
        elif line.startswith('ACC'):
            self.acc(line)
            self.type = 'ACC'
        elif line.startswith('GYR'):
            self.gyr(line)
            self.type = 'GYR'

    def gps(self, line, pre_gnss=None):
        # GPS, 时间戳(ms), lon, lat, alt, radius, bearing, speed, utc_time
        assert isinstance(line, str) and line.startswith('GPS')
        _items = line.strip().split(',')
        self.ts_ms = float(_items[1])
        self.lon = float(_items[2])
        self.lat = float(_items[3])
        self.alt = float(_items[4])
        self.radius = float(_items[5])
        self.bearing = float(_items[6])
        self.speed = float(_items[7])
        self.utc_time = float(_items[8])

        # @property
        # def loc_wgs84_str(self):
        #     return '%.6f,%.6f' % (self.lon, self.lat)

        # # @property
        # # def loc_gcj02_str(self):
        # #     return '%.6f,%.6f' % (self.lon_gcj02, self.lat_gcj02)

        # @property
        # def loc_speed(self):
        #     # if self.pre_gnss is None:
        #     #     return -1
        #     # pre_spd = geo_util.distance(self.lon, self.lat, self.pre_gnss.lon, self.pre_gnss.lat)
        #     # return max(0.0, min(33.0, pre_spd))
        #     return self.speed

        # def __repr__(self):
        #     return '%.3f,%.6f,%.6f,%.3f,%.3f' % (self.app_ts, self.lon, self.lat, self.bearing, self.speed)

    def acc(self, line):
        # ACC, 时间戳(ms), ax, ay, az
        assert isinstance(line, str) and line.startswith('ACC')
        _items = line.strip().split(',')
        self.ts_ms = float(_items[1])
        self.ax = round(float(_items[2]), 6)
        self.ay = round(float(_items[3]), 6)
        self.az = round(float(_items[4]), 6)

        # @property
        # def sen_x(self):
        #     return self.acc_x

        # @property
        # def sen_y(self):
        #     return self.acc_y

        # @property
        # def sen_z(self):
        #     return self.acc_z

        # def __repr__(self):
        #     return '%.3f,%.3f,%.3f,%.3f' % (self.app_ts, self.acc_x, self.acc_y, self.acc_z)

    def gyr(self, line):
        # GYR, 时间戳(ms), gx, gy, gz
        assert isinstance(line, str) and line.startswith('GYR')
        _items = line.strip().split(',')
        self.ts_ms = float(_items[1])
        self.gx = round(float(_items[2]), 6)
        self.gy = round(float(_items[3]), 6)
        self.gz = round(float(_items[4]), 6)

        # @property
        # def sen_x(self):
        #     return self.gyr_x

        # @property
        # def sen_y(self):
        #     return self.gyr_y

        # @property
        # def sen_z(self):
        #     return self.gyr_z

        # def __repr__(self):
        #     return '%.3f,%.3f,%.3f,%.3f' % (self.app_ts, self.gyr_x, self.gyr_y, self.gyr_z)


class DataUnit:
    def __init__(self, timestamp, data):
        self.timestamp = timestamp
        self.data = data
