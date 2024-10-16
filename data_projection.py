#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Time       : 2024/10/16 12:06
@Author     : suyufei
@File       : data_struct.py
@DevTool    : PyCharm
"""


import os
import sys
import numpy as np
import copy

import data_struct

def split_trace_sen_via_sec(trace_sen_units):
    trace_sec_units = {}
    for u in trace_sen_units:
        if u.ts_gps in trace_sec_units:
            trace_sec_units[u.ts_gps].append(u)
        else:
            trace_sec_units[u.ts_gps] = [u]
    ts_gps_list = sorted(trace_sec_units.keys())
    return trace_sec_units, ts_gps_list


def capture_stationary_frames(trace_sen_units):
    stationary_accel_units = []

    pre_gnss_unit = None
    sec_accel_units = []

    for unit in trace_sen_units:
        if isinstance(unit.obj, data_struct.GnssUnit):
            if pre_gnss_unit is None:
                pre_gnss_unit = unit.obj
                sec_accel_units = []
            else:
                if pre_gnss_unit.spd < 1e-4 and unit.obj.spd < 1e-4:
                    stationary_accel_units.extend(sec_accel_units)
                pre_gnss_unit = unit.obj
                sec_accel_units = []
        elif isinstance(unit.obj, data_struct.AccelUnit):
            sec_accel_units.append(unit.obj)

    return stationary_accel_units


def capture_accelerated_frames(trace_sen_units, accelerated_spd=1.0):
    accelerated_accel_units = []

    pre_gnss_unit = None
    sec_accel_units = []

    for unit in trace_sen_units:
        if isinstance(unit.obj, data_struct.GnssUnit):
            if pre_gnss_unit is None:
                pre_gnss_unit = unit.obj
                sec_accel_units = []
            else:
                if unit.obj.spd - pre_gnss_unit.spd > accelerated_spd:
                    accelerated_accel_units.extend(sec_accel_units)
                pre_gnss_unit = unit.obj
                sec_accel_units = []
        elif isinstance(unit.obj, data_struct.AccelUnit):
            sec_accel_units.append(unit.obj)

    return accelerated_accel_units


def capture_changed_frames(trace_sen_units, changed_spd=1.0):
    changed_accel_units = []
    changed_bitmaps = []

    pre_pre_gnss_unit = None
    pre_gnss_unit = None
    sec_accel_units = []

    for unit in trace_sen_units:
        if isinstance(unit.obj, data_struct.GnssUnit):
            if pre_pre_gnss_unit is None:
                pre_pre_gnss_unit = unit.obj
            elif pre_gnss_unit is None:
                pre_gnss_unit = unit.obj
                sec_accel_units = []
            else:
                if abs(unit.obj.spd - pre_gnss_unit.spd) >= changed_spd and \
                        (unit.obj.spd - pre_gnss_unit.spd) * (pre_gnss_unit.spd - pre_pre_gnss_unit.spd) >= 0 and \
                        800 <= unit.obj.timestamp - pre_gnss_unit.timestamp <= 1200 and \
                        800 <= pre_gnss_unit.timestamp - pre_pre_gnss_unit.timestamp <= 1200:
                    changed_accel_units.extend(sec_accel_units)
                    changed_bitmaps.extend([(unit.obj.spd - pre_gnss_unit.spd) / abs(unit.obj.spd - pre_gnss_unit.spd)] \
                                           * len(sec_accel_units))
                pre_pre_gnss_unit = pre_gnss_unit
                pre_gnss_unit = unit.obj
                sec_accel_units = []
        elif isinstance(unit.obj, data_struct.AccelUnit):
            sec_accel_units.append(unit.obj)

    return changed_accel_units, changed_bitmaps


def capture_trace_gravity(trace_sen_units):
    """ 基于静止态的多帧加速度计数据，
    利用拉格朗日乘数法（Lagrange Multiplier）求解Android手机不同姿态下重力反方向的单位向量
    """
    stationary_accel_units = capture_stationary_frames(trace_sen_units)

    if len(stationary_accel_units) == 0:
        stationary_accel_units = [u.obj for u in trace_sen_units if isinstance(u.obj, data_struct.AccelUnit)]

    Gs = [np.sqrt(np.power(u.senx, 2) + np.power(u.seny, 2) + np.power(u.senz, 2))
          for u in stationary_accel_units]
    G = np.percentile(Gs, 50)

    Fs = [np.array([u.senx, u.seny, u.senz]) / np.linalg.norm([u.senx, u.seny, u.senz])
          for u in stationary_accel_units]
    Fs = np.array(Fs)
    f1 = np.sum(Fs[:, 0])
    f2 = np.sum(Fs[:, 1])
    f3 = np.sum(Fs[:, 2])

    double_lambda = np.sqrt(np.power(f1, 2) + np.power(f2, 2) + np.power(f3, 2))
    g1 = f1 / double_lambda
    g2 = f2 / double_lambda
    g3 = f3 / double_lambda
    print(g1, g2, g3)

    return g1, g2, g3, G


def capture_trace_acceleration(trace_sen_units, accelerated_spd=1.0,
                               trace_gvtx=0.0, trace_gvty=9.8, trace_gvtz=0.0):
    """ 类似函数@link capture_trace_gravity
    基于加速态的多帧加速度计数据，利用拉格朗日乘数法解析Android手机（车辆）前进方向
    （代码中省略了推导过程 ...）
    """
    # accelerated_accel_units = capture_accelerated_frames(trace_sen_units, accelerated_spd=accelerated_spd)
    # print(len(accelerated_accel_units))
    #
    # r1 = np.sum([u.senx - trace_gvtx for u in accelerated_accel_units])
    # r2 = np.sum([u.seny - trace_gvty for u in accelerated_accel_units])
    # r3 = np.sum([u.senz - trace_gvtz for u in accelerated_accel_units])
    # print(r1, r2, r3)
    #
    # a1 = r1 / np.sqrt(np.power(r1, 2) + np.power(r2, 2) + np.power(r3, 2))
    # a2 = r2 / np.sqrt(np.power(r1, 2) + np.power(r2, 2) + np.power(r3, 2))
    # a3 = r3 / np.sqrt(np.power(r1, 2) + np.power(r2, 2) + np.power(r3, 2))
    # print(a1, a2, a3)

    changed_accel_units, changed_bitmaps = capture_changed_frames(trace_sen_units, changed_spd=accelerated_spd)
    print(len(changed_accel_units))

    r1 = np.sum([(u.senx - trace_gvtx) * b for u, b in zip(changed_accel_units, changed_bitmaps)])
    r2 = np.sum([(u.seny - trace_gvty) * b for u, b in zip(changed_accel_units, changed_bitmaps)])
    r3 = np.sum([(u.senz - trace_gvtz) * b for u, b in zip(changed_accel_units, changed_bitmaps)])
    print(r1, r2, r3)

    a1 = r1 / np.sqrt(np.power(r1, 2) + np.power(r2, 2) + np.power(r3, 2))
    a2 = r2 / np.sqrt(np.power(r1, 2) + np.power(r2, 2) + np.power(r3, 2))
    a3 = r3 / np.sqrt(np.power(r1, 2) + np.power(r2, 2) + np.power(r3, 2))
    print(a1, a2, a3)

    accelerated_x, accelerated_y, accelerated_z = a1, a2, a3
    return accelerated_x, accelerated_y, accelerated_z


def gen_projection_coord(trace_sen_units, accelerated_spd=1.0):
    """ 保证X轴朝右、Y轴朝前
    """
    g1, g2, g3, G = capture_trace_gravity(trace_sen_units)
    accelerated_x, \
    accelerated_y, \
    accelerated_z = capture_trace_acceleration(trace_sen_units, accelerated_spd=accelerated_spd,
                                               trace_gvtx=g1 * G, trace_gvty=g2 * G, trace_gvtz=g3 * G)

    Z = np.array([g1, g2, g3])
    Y = np.array([accelerated_x, accelerated_y, accelerated_z])
    X = np.cross(Y, Z)
    X = X / np.linalg.norm(X)
    print(X, Y, Z)

    print_formatted(X, Y, Z)

    return X, Y, Z


def print_formatted(X, Y, Z):
    for i, x in enumerate(X):
        print(f"X[{i}] = {x};")
    for i, y in enumerate(Y):
        print(f"Y[{i}] = {y};")
    for i, z in enumerate(Z):
        print(f"Z[{i}] = {z};")

def gen_naive_projection_coord(trace_sen_units):
    g1, g2, g3, G = capture_trace_gravity(trace_sen_units)

    Z = np.array([g1, g2, g3])
    Z = Z / np.linalg.norm(Z)
    X = np.cross(Z, [0, 1, 0])
    X = -X / np.linalg.norm(X)
    Y = np.cross(Z, X)
    Y = Y / np.linalg.norm(Y)
    print(X, Y, Z)
    return X, Y, Z


def project_imu(obj, X=None, Y=None, Z=None):
    prj_ax = np.dot(np.array([obj.senx, obj.seny, obj.senz]), X)
    prj_ay = np.dot(np.array([obj.senx, obj.seny, obj.senz]), Y)
    prj_az = np.dot(np.array([obj.senx, obj.seny, obj.senz]), Z)

    prj_obj = copy.deepcopy(obj)
    prj_obj.senx = prj_ax
    prj_obj.seny = prj_ay
    prj_obj.senz = prj_az

    return prj_obj
