# -*- coding: utf-8 -*-

# 이전 버전
# from Follow import Follow
# Follow(use_gpu=True, use_nao=True, nao_ip="10.1.22.52").process_cam()

from Draw import Draw

default_ip = "127.0.0.1"
default_port = 9559
uit8F_ai_sw_robot_ip = "10.1.22.52"

Draw(use_nao=True, nao_ip=default_ip, port=default_port,
     use_mirror=False, use_nao_cam=False).process_cam()
