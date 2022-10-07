#! /usr/bin/env python
# -*- encoding: UTF-8 -*-
"""
nao를 좌표로 움직일 수 있게 할 수 있게 하는 모듈
====

"""
import time
from AngleMath import *
import numpy as np
import math


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
    absolute_value = before_angle - now_angle if before_angle > now_angle else now_angle - before_angle
    power = float(hyperbolicTan(absolute_value))
    return power, absolute_value


def action_r_shourlder(a, b, neck_pos, middle_heap_pos, sleep_time, motion_service, power):
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

    if angle >= to_radian(18):
        motion_service.setAngles("RShoulderPitch", to_radian(90), 1.0)
    elif angle <= to_radian(-76):
        # 기준점이 완전히 바뀌기 때문에 바뀌는 코드를 적어야된다
        motion_service.setAngles("RShoulderPitch", to_radian(-90), 1.0)
    else:
        motion_service.setAngles("RShoulderPitch", to_radian(90), 1.0)

    motion_service.setAngles("RShoulderRoll", angle, power)

    time.sleep(sleep_time)


def action_r_elbow(a, b, r_shoulder_pos, r_elbow_pos, sleep_time, motion_service, power):
    """다리가 고정된 상태에서 오른팔을 좌표로 움직일 수 있는 함수

    :param a:
    :param b:
    :param sleep_time:
    :param motion_service:
    :param power:
    :return:
    """

    r_shoulder_roll_zero_bench_angle = to_nao_roll_radain2d(a, b)
    shoulder_roll_zero_bench_angle = to_nao_roll_radain2d(r_shoulder_pos, r_elbow_pos)
    angle = r_shoulder_roll_zero_bench_angle - shoulder_roll_zero_bench_angle
    motion_service.setAngles("RElbowYaw", to_radian(0), 1.0)
    motion_service.setAngles("RElbowRoll", angle, power)
    motion_service.setAngles("RWristYaw", to_radian(90), 1.0)
    # if angle >= to_radian(18):
    #     motion_service.setAngles("RElbowRoll", to_radian(18), power)
    # elif angle <= to_radian(-76):
    #     # 기준점이 완전히 바뀌기 때문에 바뀌는 코드를 적어야된다
    #     motion_service.setAngles("RElbowRoll", to_radian(-76), power)
    # else:
    #     #motion_service.setAngles("RElbowPitch", to_radian(90), 1.0)


    time.sleep(sleep_time)


def action_l_shourlder(a, b, neck_pos, mid_hip_pos, sleep_time, motion_service, power):
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
    
    if angle >= to_radian(76):
        motion_service.setAngles("LShoulderPitch", to_radian(-90), 1.0)
    elif angle <= to_radian(-18):
        motion_service.setAngles("LShoulderPitch", to_radian(90), 1.0)
    else:
        motion_service.setAngles("LShoulderPitch", to_radian(90), 1.0)
    motion_service.setAngles("LShoulderRoll", angle, power)

    time.sleep(sleep_time)
