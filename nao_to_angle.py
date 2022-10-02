#! /usr/bin/env python
# -*- encoding: UTF-8 -*-
"""
nao를 좌표로 움직일 수 있게 할 수 있게 하는 모듈
====

"""
import time

import qi
import argparse
import sys
import almath
import numpy as np
import math


def to_middle_xy(a, b):
    """a를 중점으로 하는 b의 좌표를 리턴

    :param a:
        almath.Position2D 객체
    :param b:
        almath.Position2D 객체
    :return:
        b - a
    """
    return b - a


def get_to_radian(a, b):
    """라디안값을 추출하는 함수 리턴

    :param a:
        almath.Position2D 객체
    :param b:
        almath.Position2D 객체
    :return:
        -pi~+pi 를 가지는 각도로 반환(거리 없음) 반환
    """
    r = to_middle_xy(a, b)

    x, y = r.x, r.y

    if x > 0:
        return math.atan(y / x)
    elif x < 0 and y >= 0:
        return math.atan(y / x) + math.pi
    elif x < 0 and y < 0:
        return math.atan(y / x) - math.pi
    elif x == 0 and y > 0:
        return math.pi / 2
    elif x == 0 and y < 0:
        return -math.pi / 2
    else:
        return 0


def get_to_radian2d(a, b):
    """
    라디안값을 추출하는 함수 리턴 0 ~ 2pi
    :param a:
    :param b:
    :return:
        0 ~ 2pi를 가지는 각도로 반환(거리 없음) 반환
    """
    r = to_middle_xy(a, b)

    x, y = r.x, r.y

    if x > 0 and y >= 0:
        return math.atan(y / x)
    elif x > 0 and y < 0:
        return math.atan(y / x) + math.pi * 2
    elif x < 0:
        return math.atan(y / x) + math.pi
    elif x == 0 and y > 0:
        return math.pi / 2
    elif x == 0 and y < 0:
        return math.pi * 3 / 2
    else:
        return -1


def reversal_way_angle(angle):
    """기준점의 시작 방향을 반대로 바꾼다
    :param angle:   각도
    :return: 2pi-angle

    """
    return math.pi * 2 - angle


def change_zero_benchmark(angle, change_angle):
    """극 좌표계 angle의 0의 기준을 changeAngle로 변환한다
    :param angle:
    :param change_angle:
    :return:    좌표계의 angle의 기준을 changeAngle로 바꾼 값을 전달
    """
    angle -= change_angle

    if angle < 0:
        angle = 2 * math.pi + angle

    if angle >= 2 * math.pi:
        angle -= 2 * math.pi

    return angle


def to_nao_shourlder_radain2d(a, b):
    """다리가 고정인 상태에서 팔을 움직일 수 있게함

    :param a:
    :param b:
    :return:
        nao 좌표계로 기준을 정렬을 한다
    """
    angle = get_to_radian2d(a, b)
    angle = change_zero_benchmark(angle, math.pi * 3 / 2)
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
    before_angle = to_nao_shourlder_radain2d(before_a, before_b)
    now_angle = to_nao_shourlder_radain2d(now_a, now_b)
    absolute_value = before_angle - now_angle if before_angle > now_angle else now_angle - before_angle
    power = float(hyperbolicTan(absolute_value))
    return power, absolute_value


def action_r_shourlder(a, b, sleep_time, motion_service, power):
    """다리가 고정된 상태에서 오른팔을 좌표로 움직일 수 있는 함수

    :param a:
    :param b:
    :param sleep_time:
    :param motion_service:
    :param power:
    :return:
    """

    angle = to_nao_shourlder_radain2d(a, b)

    if angle >= 18 * almath.TO_RAD:
        motion_service.setAngles("RShoulderRoll", 18 * almath.TO_RAD, power)
    elif angle <= -76 * almath.TO_RAD:
        # 기준점이 완전히 바뀌기 때문에 바뀌는 코드를 적어야된다
        motion_service.setAngles("RShoulderRoll", -76 * almath.TO_RAD, power)
    else:
        motion_service.setAngles("RShoulderPitch", 90 * almath.TO_RAD, 1.0)
        motion_service.setAngles("RShoulderRoll", angle, power)

    time.sleep(sleep_time)




def action_l_shourlder(a, b, sleep_time, motion_service, power):
    """다리가 고정된 상태에서 왼팔을 좌표로 움직일 수 있는 함수
    
    :param a: 
    :param b: 
    :param sleep_time: 
    :param motion_service: 
    :param power: 
    :return: 
    """
    angle = to_nao_shourlder_radain2d(a, b)

    if angle >= 76 * almath.TO_RAD:
        motion_service.setAngles("LShoulderRoll", 76 * almath.TO_RAD, power)
    elif angle <= -18 * almath.TO_RAD:
        motion_service.setAngles("LShoulderRoll", -18 * almath.TO_RAD, power)
    else:
        motion_service.setAngles("LShoulderPitch", 90 * almath.TO_RAD, 1.0)
        motion_service.setAngles("LShoulderRoll", angle, power)

    time.sleep(sleep_time)



def main(session):
    motion_service = session.service("ALMotion")
    posture_service = session.service("ALRobotPosture")

    motion_service.wakeUp()
    posture_service.goToPosture("Stand", 1)

    # 2d 상에서 좌표 계산 y z 축을 사용 한다
    #                       x  y
    a = almath.Position2D(-10, 25)
    b = almath.Position2D(-20, 20)

    print a, b

    action_r_shourlder(a, b, 1, motion_service)
    b.x += 5
    action_r_shourlder(a, b, 1, motion_service)
    b.x -= 5
    action_r_shourlder(a, b, 1, motion_service)

    motion_service.rest()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="10.1.17.95",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    my_session = qi.Session()

    args.ip = "127.0.0.1"
    try:
        my_session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip +
               "\" on port " + str(args.port) + ".\n" +
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    main(my_session)
