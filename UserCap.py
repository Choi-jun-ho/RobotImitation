# coding=utf-8
class UserCap(object):
    def __init__(self, img):
        """cv2 cap 형식과 비슷하게 사용하려고 만든 클래스
        read, isOpened 전부 True를 내보냄
        :param img:
            한장의 사진
        """
        self.img = img

    def read(self):
        """open cv의 cap.read()와 같은 형식을 return 하는 함수
        :return:
            True, 이미지
        """
        return True, self.img

    @staticmethod
    def isOpened():
        """open cv의 cap.isOpened()와 같은 형식을 return 하는 함수
        :return:
            True
        """
        return True
