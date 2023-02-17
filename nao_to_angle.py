#! /usr/bin/env python
# -*- encoding: UTF-8 -*-
"""
nao를 좌표로 움직일 수 있게 할 수 있게 하는 모듈
====

"""
import time

import almath

from AngleMath import *
import numpy as np
import math
from MotionData import MotionData


def to_nao_roll_radain2d(a, b):
    """다리가 고정인 상태에서 팔을 움직일 수 있게함

    :param a:
    :param b:
    :return:
        nao 좌표계로 기준을 정렬을 한다
    """
    angle = get_to_radian2d(a, b)
    # 몸체 각도

    # 몸체 각도 - 팔 각도 -> 저장 필요

    angle = zero_benchmark_roll(angle)
    # 기준점 정렬 완료 상태, +- 상태로 변환 해야 된다

    if angle <= math.pi:
        return angle
    else:
        result = (angle - math.pi) - math.pi
        return result


def hyperbolicTan(x):
    return (np.exp(x) - np.exp(-x)) / (np.exp(x) + np.exp(-x))


def before_now_get_power(before_a, before_b, now_a, now_b):
    """
    :param before_a:
    :param before_b:
    :param now_a:
    :param now_b:
    :return:
        power:nao에게 주어진 power, absolute_value:|before_angle - now_angle|
    """
    before_angle = to_nao_roll_radain2d(before_a, before_b)
    now_angle = to_nao_roll_radain2d(now_a, now_b)
    absolute_value = abs(before_angle - now_angle)
    # power = 0.1 + 0.9*absolute_value*almath.TO_DEG*10/35.66
    return 1, absolute_value


def action_r_shourlder(a, b, neck_pos, middle_heap_pos, power):
    """다리가 고정된 상태에서 오른팔을 좌표로 움직일 수 있는 함수

    :param a:
    :param b:
    :param sleep_time:
    :param motion_service:
    :param power:
    :return:
    """

    r_shoulder_roll_zero_bench_angle = to_nao_roll_radain2d(a, b)
    body_shoulder_roll_zero_bench_angle = to_nao_roll_radain2d(neck_pos, middle_heap_pos)
    angle = r_shoulder_roll_zero_bench_angle - body_shoulder_roll_zero_bench_angle

    r_shoulder_motion_data = MotionData()

    if angle <= to_radian(-76):
        # 기준점이 완전히 바뀌기 때문에 바뀌는 코드를 적어야된다
        # motion_service.setAngles("RShoulderPitch", to_radian(-90), 1.0)
        # motion_service.setAngles("RShoulderRoll", -angle-to_radian(180), power)
        r_shoulder_motion_data.parts_name.extend(["RShoulderPitch", "RShoulderRoll"])
        r_shoulder_motion_data.angles.extend([to_radian(-90), -angle - to_radian(180)])
        r_shoulder_motion_data.speeds.extend([1.0, power])
    else:
        # motion_service.setAngles("RShoulderPitch", to_radian(90), 1.0)
        # motion_service.setAngles("RShoulderRoll", angle, power)
        r_shoulder_motion_data.parts_name.extend(["RShoulderPitch", "RShoulderRoll"])
        r_shoulder_motion_data.angles.extend([to_radian(90), angle])
        r_shoulder_motion_data.speeds.extend([1.0, power])

    return r_shoulder_motion_data


def action_r_elbow(a, b, r_shoulder_pos, r_elbow_pos, power):
    """다리가 고정된 상태에서 오른팔을 좌표로 움직일 수 있는 함수

    :param a:
    :param b:
    :param sleep_time:
    :param motion_service:
    :param power:
    :return:
    """

    r_elobw_roll_zero_bench_angle = to_nao_roll_radain2d(a, b)
    r_shoulder_roll_zero_bench_angle = to_nao_roll_radain2d(r_shoulder_pos, r_elbow_pos)
    angle = r_elobw_roll_zero_bench_angle - r_shoulder_roll_zero_bench_angle

    r_elbow_motion_data = MotionData()

    # motion_service.setAngles("RElbowYaw", to_radian(0), 1.0)
    # motion_service.setAngles("RElbowRoll", angle, power)
    # motion_service.setAngles("RWristYaw", to_radian(90), 1.0)

    r_elbow_motion_data.parts_name.extend(["RElbowYaw", "RElbowRoll", "RWristYaw"])
    r_elbow_motion_data.angles.extend([to_radian(0), angle, to_radian(90)])
    r_elbow_motion_data.speeds.extend([1.0, power, 1.0])

    # if angle >= to_radian(18):
    #     motion_service.setAngles("RElbowRoll", to_radian(18), power)
    # elif angle <= to_radian(-76):
    #     # 기준점이 완전히 바뀌기 때문에 바뀌는 코드를 적어야된다
    #     motion_service.setAngles("RElbowRoll", to_radian(-76), power)
    # else:
    #     #motion_service.setAngles("RElbowPitch", to_radian(90), 1.0)

    return r_elbow_motion_data


def action_l_shourlder(a, b, neck_pos, mid_hip_pos, power):
    """다리가 고정된 상태에서 왼팔을 좌표로 움직일 수 있는 함수
    
    :param a: 
    :param b: 
    :param sleep_time: 
    :param motion_service: 
    :param power: 
    :return: 
    """
    l_shoulder_roll_angle = to_nao_roll_radain2d(a, b)
    body_roll_angle = to_nao_roll_radain2d(neck_pos, mid_hip_pos)
    angle = l_shoulder_roll_angle - body_roll_angle

    l_shoulder_motion_data = MotionData()

    if angle >= to_radian(76):
        # motion_service.setAngles("LShoulderPitch", to_radian(-90), 1.0)
        # motion_service.setAngles("LShoulderRoll", to_radian(180)-angle, power)
        l_shoulder_motion_data.parts_name.extend(["LShoulderPitch", "LShoulderRoll"])
        l_shoulder_motion_data.angles.extend([to_radian(-90), to_radian(180) - angle])
        l_shoulder_motion_data.speeds.extend([1.0, power])
    else:
        # motion_service.setAngles("LShoulderPitch", to_radian(90), 1.0)
        # motion_service.setAngles("LShoulderRoll", angle, power)

        l_shoulder_motion_data.parts_name.extend(["LShoulderPitch", "LShoulderRoll"])
        l_shoulder_motion_data.angles.extend([to_radian(90), angle])
        l_shoulder_motion_data.speeds.extend([1.0, power])

    return l_shoulder_motion_data


def action_l_elbow(a, b, l_shoulder_pos, l_elbow_pos, power):
    """다리가 고정된 상태에서 오른팔을 좌표로 움직일 수 있는 함수

    :param a:
    :param b:
    :param sleep_time:
    :param motion_service:
    :param power:
    :return:
    """

    l_elbow_roll_zero_bench_angle = to_nao_roll_radain2d(a, b)
    l_shoulder_roll_zero_bench_angle = to_nao_roll_radain2d(l_shoulder_pos, l_elbow_pos)
    angle = l_elbow_roll_zero_bench_angle - l_shoulder_roll_zero_bench_angle

    # motion_service.setAngles("LElbowYaw", to_radian(0), 1.0)
    # motion_service.setAngles("LElbowRoll", angle, power)
    # motion_service.setAngles("LWristYaw", to_radian(-90), 1.0)

    l_elbow_motion_data = MotionData()
    l_elbow_motion_data.parts_name.extend(["LElbowYaw", "LElbowRoll", "LWristYaw"])
    l_elbow_motion_data.angles.extend([to_radian(0), angle, to_radian(-90)])
    l_elbow_motion_data.speeds.extend([1.0, power, 1.0])

    return l_elbow_motion_data
