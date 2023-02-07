# -*- coding:utf-8 -*-
import time

import qi
import sys
import almath
import nao_to_angle as nta
import vision_definitions
import numpy
import Skeleton
from UserCap import UserCap
from datetime import datetime
from MotionData import MotionData

class Nao:
    def __init__(self, nao_ip="127.0.0.1", port=9559, use_nao_cam=False):
        """
        Nao 와 관련된 것들을 관리하는 클래스
        :param nao_ip:
            nao와 연결하려는 ip, default:127.0.0.1
        :param port:
            nao와 연결하려는 port, default:9559
        """
        self.__session = qi.Session()

        self.__use_nao_cam = use_nao_cam
        self.__nao_ready(nao_ip, port)
        self.__beforePoints = None

    def __connect(self, ip, port):
        """Nao와 연결할때 사용하는 함수

            로봇과 같은 ip를 사용해야함(wifi 같은 걸로)
        :param ip:
        :param port:
        :return:
        """
        try:
            self.__session.connect("tcp://" + ip + ":" + str(port))
        except RuntimeError:
            print("같은 와이파이를 사용")
            sys.exit(1)

    def __set_service(self):
        """로봇과 관련된 api를 기본적으로 세팅해주는 함수

        motion_service : 움직임관련
        posture_service : 포즈 관련
        video_service : 비디오 관련


        :return:
        """
        self.__motion_service = self.__session.service("ALMotion")
        self.__posture_service = self.__session.service("ALRobotPosture")

        #print self.__use_nao_cam
        if self.__use_nao_cam is True:
            self.__video_service = self.__session.service("ALVideoDevice")

            resolution = vision_definitions.kQVGA
            color_space = vision_definitions.kBGRColorSpace
            fps = 30

            # 등록된 게 있다면 전부 제거후 등록
            for client in self.__video_service.getSubscribers():
                self.__video_service.unsubscribe(client)

            self.__video_service.setActiveCamera('_client', 0)
            self._imgClient = self.__video_service.subscribe("_client", resolution, color_space, fps)

            self.__video_service.setParam(vision_definitions.kCameraSelectID, 0)

            self.__video_service.setActiveCamera('_client', 0)

        self.__motion_service.wakeUp()
        self.__posture_service.goToPosture("Stand", 1)

    def __nao_ready(self, ip, port):
        self.__connect(ip, port)
        self.__set_service()
        self.relbow_com_roll = self.__motion_service.getPosition("RElbowRoll", 1, True)

    def get_video_capture(self):
        """나오 카메라를 사용할 때 open_cv.cap()과 같은 형식으로 주기 위해 필요한 함수

        :return: cv.cap()의 return 값인 이미지 여부와 이미지를 리턴
        """
        nao_image = self.__video_service.getImageRemote(self._imgClient)

        # 나오의 이미지와 cv2의 이미지가 다르며 이를 바꿔 줘야 함
        nao_image_pixel = numpy.frombuffer(nao_image[6], dtype='%iuint8' % nao_image[2])

        img = (numpy.reshape(nao_image_pixel,
                             (nao_image[1], nao_image[0], nao_image[2])))

        cap = UserCap(img)
        return cap

    def is_points(self, points, a, b, parts):
        """

        :param points:  Skeleton을 예측했을 때 각 위치들
        :param a:   Skeleton의 처음 좌표에 해당하는 번호
        :param b:   Skeleton의 마지막 좌표에 해당하는 번호
        :param parts:   Skeleton의 부위 이름
        :return:    각 Point가 있으면 True

        """
        is_skeleton_parts = False
        if self.is_skeleton_parts(points, a, b):
            is_skeleton_parts = True
        if is_skeleton_parts and not self.__motion_service.getIdlePostureEnabled(parts):
            return True
        return False

    @staticmethod
    def is_skeleton_parts(points, a, b):
        a_index = Skeleton.Skeleton.BODY_PARTS[a]
        b_index = Skeleton.Skeleton.BODY_PARTS[b]
        is_body_index = False
        if points[a_index] is not None and points[b_index] is not None:
            is_body_index = True
        return is_body_index

    def is_before_points(self, a, b):
        """
        :param a:   Skeleton의 이전 좌표의 처음 좌표에 해당하는 번호
        :param b:   Skeleton의 이전 좌표의 마지막 좌표에 해당하는 번호
        :return:    각 Point가 있으면 True

        """
        if self.__beforePoints is not None \
                and self.__beforePoints[a] is not None and self.__beforePoints[b] is not None:
            return True
        return False

    @staticmethod
    def to2d_position(points, a):
        """almath.Position2D 객체로 바꿔주는 함수
        :param points:
        :param a:
        :return: points의 a를 almath.Position2D 객체로 리턴
        """
        return almath.Position2D(points[a][0], -1 * points[a][1])

    def get_power_and_absolute_value(self, points, a_name, b_name, parts):
        """현재의 좌표와 적절한 힘과 이전과 현재의 차에대한 절댓값을 반환 하는 함수

        :param points:
        :param a:
        :param b:
        :param parts:
        :return:
        """
        if self.is_points(points, a_name, b_name, parts):

            power = 0.2
            absolute_value = 0.2  # 이전값과 절대적인 차이를 말함 차이가 작으면 실행 안해 조금더 부드럽게 작용
            a = Skeleton.Skeleton.BODY_PARTS[a_name]
            b = Skeleton.Skeleton.BODY_PARTS[b_name]
            now_a = self.to2d_position(points, a)
            now_b = self.to2d_position(points, b)

            if self.is_before_points(a, b):
                before_a = self.to2d_position(self.__beforePoints, a)
                before_b = self.to2d_position(self.__beforePoints, b)
                power, absolute_value = nta.before_now_get_power(before_a, before_b, now_a, now_b)

            return True, now_a, now_b, power, absolute_value
        return False, None, None, None, None


    def move_to_parts(self, points, a1, a2, parts, c1, c2, movefuntion):
        is_l_arm_points, now_a, now_b, power, absolute_value \
            = self.get_power_and_absolute_value(points, a1, a2, parts)\

        motion_data = None

        if is_l_arm_points and self.is_skeleton_parts(points, c1, c2):
            if absolute_value > 0.05:
                neck_pos = self.to2d_position(points, Skeleton.Skeleton.BODY_PARTS[c1])
                mid_hip_pos = self.to2d_position(points, Skeleton.Skeleton.BODY_PARTS[c2])
                parts_movefun = movefuntion
                motion_data = parts_movefun(now_a, now_b, neck_pos, mid_hip_pos, power=0.2 if power < 0.2 else power)
        return motion_data

    def move_to_r_arm(self, points):
        return self.move_to_parts(points, "RShoulder", "RElbow", "RArm", "Neck", "MidHip", nta.action_r_shourlder)

    def move_to_r_elbow(self, points):
        return self.move_to_parts(points, "RElbow", "RWrist", "RArm",
                                  "RShoulder", "RElbow", nta.action_r_elbow)

    def move_to_l_arm(self, points):
        return self.move_to_parts(points, "LShoulder", "LElbow", "LArm", "Neck", "MidHip", nta.action_l_shourlder)

    def move_to_l_elbow(self, points):  # 어깨와 팔꿈치, 팔꿈치와 손의 선분에 대한 각도가 힌트
        return self.move_to_parts(points, "LElbow", "LWrist", "LArm", "LShoulder", "LElbow", nta.action_l_elbow)

    def __set_point_nao(self, points):
        """Skeleton Point로 움직일 나오의 부위들을 지정하는 함수

        :param points:
        :return:
        """
        motion_data = MotionData()

        r_arm_time = datetime.now().microsecond
        motion_data.add(self.move_to_r_arm(points))
        print "rarmtime: ", datetime.now().microsecond - r_arm_time

        r_elbow_time = datetime.now().microsecond
        motion_data.add(self.move_to_r_elbow(points))
        print "relobwtime: ", datetime.now().microsecond - r_elbow_time

        l_arm_time = datetime.now().microsecond
        motion_data.add(self.move_to_l_arm(points))
        print "larmtime: ", datetime.now().microsecond - l_arm_time

        l_elbow_time = datetime.now().microsecond
        motion_data.add(self.move_to_l_elbow(points))
        print "lelobwtime: ", datetime.now().microsecond - l_elbow_time

        move_motion_time = datetime.now().microsecond
        self.angleInterpolationWithSpeed(motion_data)
        print "move_motion_time: ", datetime.now().microsecond - move_motion_time

        #time.sleep(0.01)

        self.__beforePoints = points


    def angleInterpolationWithSpeed(self, motion_data):
        print motion_data.parts_name
        print motion_data.angles
        print motion_data.speeds
        if len(motion_data.parts_name) != 0:
            # setAngles
            # angleInterpolationWithSpeed
            self.__motion_service.setAngles(motion_data.parts_name, motion_data.angles, motion_data.speeds)

    def run(self, points):
        self.__set_point_nao(points)

    def rest(self):
        self.__motion_service.rest()
