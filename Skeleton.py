# -*- coding: utf-8 -*-

import cv2

class Skeleton:
    # 사용할 인공지능 모델
    __protoFile = "model/pose/body_25/pose_deploy.prototxt"
    __weightsFile = "model/pose/body_25/pose_iter_584000.caffemodel"

    # MPI 에서 각 파트 번호, 선으로 연결될 POSE_PAIRS
    '''BODY_PARTS = {"Head": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4,
                  "LShoulder": 5, "LElbow": 6, "LWrist": 7, "RHip": 8, "RKnee": 9,
                  "RAnkle": 10, "LHip": 11, "LKnee": 12, "LAnkle": 13, "Chest": 14,
                  "Background": 15}

    POSE_PAIRS = [["Head", "Neck"], ["Neck", "RShoulder"], ["RShoulder", "RElbow"],
                  ["RElbow", "RWrist"], ["Neck", "LShoulder"], ["LShoulder", "LElbow"],
                  ["LElbow", "LWrist"], ["Neck", "Chest"], ["Chest", "RHip"], ["RHip", "RKnee"],
                  ["RKnee", "RAnkle"], ["Chest", "LHip"], ["LHip", "LKnee"], ["LKnee", "LAnkle"]]'''

    # body25 모델
    BODY_PARTS = {"Nose": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4, "LShoulder": 5, "LElbow": 6,
                  "LWrist": 7, "MidHip": 8, "RHip": 9, "RKnee": 10, "RAnkle": 11, "LHip": 12, "LKnee": 13,
                  "LAnkle": 14, "REye": 15, "LEye": 16, "REar": 17, "LEar": 18, "LBigToe": 19, "LSmallToe": 20,
                  "LHeel": 21, "RBigToe": 22, "RSmallToe": 23, "RHeel": 24, "Background": 25}

    POSE_PAIRS = [['Nose', 'Neck'], ['Nose', 'REye'], ['Nose', 'LEye'], ['Neck', 'RShoulder'], ['Neck', 'LShoulder'],
                  ['Neck', 'MidHip'], ['MidHip', 'RHip'], ['MidHip', 'LHip'], ['RHip', 'RKnee'], ['LHip', 'LKnee'],
                  ['RShoulder', 'RElbow'], ['RElbow', 'RWrist'], ['LShoulder', 'LElbow'], ['LElbow', 'LWrist'],
                  ['RKnee', 'RAnkle'], ['LKnee', 'LAnkle'], ['REye', 'REar'], ['LEye', 'LEar'], ['LAnkle', 'LHeel'],
                  ['LBigToe', 'LHeel'], ['LSmallToe', 'LHeel'], ['RAnkle', 'RHeel'], ['RBigToe', 'RHeel'],
                  ['RSmallToe', 'RHeel']]

    def __init__(self, use_gpu=True):
        """Skeleton을 모델을 관리하는 클래스
        :param use_gpu:
            gpu 사용여부, default:True
        """
        self.__predict = None
        self.__height = None
        self.__width = None
        self.points = None
        self.__frame = None
        self.__poseModel = cv2.dnn.readNetFromCaffe(self.__protoFile, self.__weightsFile)

        if use_gpu:
            self.__poseModel.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)  # GPU 사용
            self.__poseModel.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)  # GPU 사용

    def set_frame(self, frame):
        """Skeleton을 예측할 이미지
        :param frame:
        :return:
        """
        self.__frame = frame

    def set_heigh_width(self, height, width):
        self.__height = height
        self.__width = width

    def get_predict(self, frame):
        blob = cv2.dnn.blobFromImage(frame, 1.0 / 255, (self.__width, self.__height), (0, 0, 0), swapRB=True, crop=False)
        self.__poseModel.setInput(blob)
        return self.__poseModel.forward()
