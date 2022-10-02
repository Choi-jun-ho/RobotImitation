# coding=utf-8

import math
import almath


class AngleMath:

    @staticmethod
    def to_radian(angle):
        return angle*almath.TO_RAD

    @staticmethod
    def to_degree(radian):
        return radian*almath.TO_DEG

    @staticmethod
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

    @staticmethod
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

    @classmethod
    def get_to_radian2d(cls, a, b):
        """
        라디안값을 추출하는 함수 리턴 0 ~ 2pi
        :param a:
        :param b:
        :return:
            0 ~ 2pi를 가지는 각도로 반환(거리 없음) 반환
        """
        r = cls.to_middle_xy(a, b)

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

    @staticmethod
    def reversal_way_angle(angle):
        """기준점의 시작 방향을 반대로 바꾼다
        :param angle:   각도
        :return: 2pi-angle

        """
        return math.pi * 2 - angle

    @staticmethod
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
