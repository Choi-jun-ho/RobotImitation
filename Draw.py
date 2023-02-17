# -*- coding: utf-8 -*-


import cv2
import numpy as np
import pyrealsense2 as rs

from Nao import Nao
from Skeleton import Skeleton
from datetime import datetime
from UserCap import UserCap


class Draw:
    __Nao = None
    __Skeleton = None
    __points = []

    def __init__(self, use_gpu=True,
                 use_nao=False, nao_ip="127.0.0.1", port=9559,
                 use_mirror=False, use_nao_cam=False, use_realsense=False):
        """
        진입 점을 가지는 클래스
        내부에는 예측하는 것과 그리는 것이 있으며 그리는 것은 이쪽에서 관리됩니다

        :param use_gpu:
            gpu 사용 여부, default:True
        :param use_nao:
            nao 사용 여부, default:False
        :param nao_ip:
            nao 사용시 ip 지정, default:127.0.0.1
        :param port:
            nao 사용시 port 지정, default:9559
        :param use_mirror:
            mirror 모드, default:False
        :param use_nao_cam:
            nao의 cam을 사용 여부, default:False
        """
        self.__frame = None
        self.__use_nao = use_nao
        self.__use_gpu = use_gpu
        self.__Skeleton = Skeleton(self.__use_gpu)
        self.__use_mirror = use_mirror
        self.__use_realsense = use_realsense
        self.__use_nao_cam = use_nao_cam if use_nao else False

        if use_nao:
            self.__Nao = Nao(nao_ip, port, use_nao_cam)
        if use_realsense:
            # Configure depth and color streams
            self.pipeline = rs.pipeline()
            self.config = rs.config()

            # Get device product line for setting a supporting resolution
            pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
            pipeline_profile = self.config.resolve(pipeline_wrapper)
            device = pipeline_profile.get_device()
            device_product_line = str(device.get_info(rs.camera_info.product_line))

            found_rgb = False
            for s in device.sensors:
                if s.get_info(rs.camera_info.name) == 'RGB Camera':
                    found_rgb = True
                    break
            if not found_rgb:
                print("The demo requires Depth camera with Color sensor")
                exit(0)

            self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

            if device_product_line == 'L500':
                self.config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
            else:
                self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

            # Start streaming
            self.pipeline.start(self.config)
    def __draw_skeleton_position(self):
        """예측한 스켈레톤의 각각의 point 점을 그리는 함수
        :return:
        """
        self.__predict = self.__Skeleton.get_predict(self.__frame)
        h = self.__predict.shape[2]
        w = self.__predict.shape[3]

        predict = self.__predict[:, :len(self.__Skeleton.BODY_PARTS), :, :]

        assert (len(self.__Skeleton.BODY_PARTS) == predict.shape[1])

        self.__Skeleton.points = []
        for i in range(len(self.__Skeleton.BODY_PARTS)):
            # 해당 신체 부위 신뢰도 얻음.
            prob_map = predict[0, i, :, :]

            # global 최대값 찾기
            _, prob, _, point = cv2.minMaxLoc(prob_map)

            # 원래 이미지에 맞게 점 위치 변경
            x = (self.__width * point[0]) / w
            y = (self.__height * point[1]) / h

            # 키 포인트 검출한 결과가 0.1보다 크면(검출한 곳이 위 BODY_PARTS 랑 맞는 부위면) points 에 추가, 검출 했는데 부위가 없으면 None 으로
            if prob > 0.3:
                cv2.circle(self.__frame, (int(x), int(y)), 3, (0, 255, 255), thickness=-1,
                           lineType=cv2.FILLED)  # circle(그릴곳, 원의 중심, 반지름, 색)

                if self.__use_realsense:
                    cv2.putText(self.__frame, "{}".format(self.depth_image[y][x]), (int(x), int(y)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1,
                                lineType=cv2.LINE_AA)
                else:
                    cv2.putText(self.__frame, "{}".format(i), (int(x), int(y)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1,
                                lineType=cv2.LINE_AA)
                self.__Skeleton.points.append((int(x), int(y)))
            else:
                self.__Skeleton.points.append(None)

    def __draw_skeleton(self):
        """
        예측한 Skeleton의 뼈대를 Window에 그리는 함수
            예측한 것을 가져와서 opencv를 사용하여 그립니다.
        :return:
        """
        for pair in self.__Skeleton.POSE_PAIRS:
            part_a = pair[0]  # Head
            part_b = pair[1]  # Neck

            assert (part_a in self.__Skeleton.BODY_PARTS)
            assert (part_b in self.__Skeleton.BODY_PARTS)

            part_a = self.__Skeleton.BODY_PARTS[part_a]  # 0
            part_b = self.__Skeleton.BODY_PARTS[part_b]  # 1

            if self.__Skeleton.points[part_a] and self.__Skeleton.points[part_b]:
                cv2.line(self.__frame, self.__Skeleton.points[part_a], self.__Skeleton.points[part_b], (0, 255, 0), 1)

    def __process_frame(self):
        """
        한 프레임당 실행되는 함수
        :return:
        """
        self.__draw_skeleton_position()

        if self.__use_nao:
            self.__Nao.run(self.__Skeleton.points)

        self.__draw_skeleton()

    def process_cam(self):
        """
        진입점 입니다
        :return:
        """

        camera_select = 0
        if self.__use_realsense:
            camera_select = 1
        cap = cv2.VideoCapture(camera_select, cv2.CAP_DSHOW)


        if self.__use_nao_cam:
            cap = self.__Nao.get_video_capture()
        elif self.__use_realsense:
            cap = self.get_realsense()


        if not cap.isOpened():
            print ("캠을 실행할 수 없음\n", "권한 확인 또는 캠을 설치 해주시길 바랍니다")
            return

        (success, self.__frame) = cap.read()

        kernel1d = cv2.getGaussianKernel(3, 3)
        kernel2d = np.outer(kernel1d, kernel1d.transpose())
        self.__frame = cv2.filter2D(self.__frame, -1, kernel2d)

        (self.__height, self.__width) = self.__frame.shape[:2]

        if self.__use_mirror:
            self.__frame = cv2.cuda.flip(self.__frame, 1)

        self.__Skeleton.set_frame(self.__frame)
        self.__Skeleton.set_heigh_width(self.__height, self.__width)

        while success:

            self.__process_frame()
            # t, _ = self.__poseModel.getPerfProfile()
            # freq = cv2.getTickFrequency() / 1000
            # cv2.putText(self.__frame, '%.2fms' % (t / freq), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))
            cv2.imshow("Output", self.__frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q") or key == 27:
                break

            if self.__use_nao_cam:
                cap = self.__Nao.get_video_capture()
            elif self.__use_realsense:
                cap = self.get_realsense()

            (success, self.__frame) = cap.read()

            filter_time = datetime.now().microsecond
            self.__frame = cv2.filter2D(self.__frame, -1, kernel2d)

            if self.__use_mirror:
                self.__frame = cv2.cuda.flip(self.__frame, 1)
            self.__Skeleton.set_frame(self.__frame)

        if self.__use_nao:  # Nao 사용시 끝날때 나오 휴식
            self.__Nao.rest()
        else:
            cap.release()

        cv2.destroyAllWindows()

    def get_realsense(self):
        frames = self.pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        depth_colormap_dim = depth_colormap.shape
        color_colormap_dim = color_image.shape

        # If depth and color resolutions are different, resize color image to match depth image for display
        if depth_colormap_dim != color_colormap_dim:
            resized_color_image = cv2.resize(color_image, dsize=(depth_colormap_dim[1], depth_colormap_dim[0]),
                                             interpolation=cv2.INTER_AREA)
            images = resized_color_image
        else:
            images = color_image

        cap = UserCap(images)
        self.depth_image = depth_image

        return cap
