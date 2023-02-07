import matplotlib.pyplot as plt
from datetime import datetime

import numpy as np


class SaveData:
    traking_joints = None
    human_joints_save_of_time = []
    robot_joints_save_of_time = []
    diff_joint_save = []
    time_of_robot_save = []
    human_time_save = []
    time_human_robot_diff = []
    start_time = None

    def __init__(self):
        self.start_time = datetime.now().microsecond

    def set_tarking_joints(self, traking_joints):
        self.traking_joints = traking_joints

    def set_start_time(self):
        self.start_time = datetime.now().microsecond

    def traking_time_huan_robot_diff(self, time):
        self.time_human_robot_diff += time

    def traking_human_joint(self, joint):
        self.human_time_save += self.start_time - datetime.now().microsecond
        self.human_joints_save_of_time += joint

    def traking_robot_joint(self, joint):
        self.time_of_robot_save += self.start_time - datetime.now().microsecond
        self.robot_joints_save_of_time += joint

    def show(self):

        human_joint_sum = []
        for human_joints in self.human_joints_save_of_time:
            human_joint_sum += np.array(human_joints).sum()

        robot_joint_sum = []
        for robot_joints in self.robot_joints_save_of_time:
            robot_joint_sum += np.array(robot_joints).sum()

        human_robot_joint_diff = []
        for i in range(len(human_joint_sum)):
            human_robot_joint_diff += abs(human_joint_sum[i] - robot_joint_sum[i])

        time = []
        for i in range(len(self.human_time_save)):
            time += self.human_time_save[i] - self.time_human_robot_diff

        plt.plot(human_joint_sum, self.human_time_save, 'bo--')
        plt.plot(robot_joint_sum, self.time_of_robot_save, 'ro--')
        plt.plot(human_robot_joint_diff, time, 'go--')
        plt.show()
