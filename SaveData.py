import math
import time

import almath
import matplotlib.pyplot as plt


class SaveData:
    human_joints_save_of_time = []
    robot_joints_save_of_time = []
    diff_joint_save = []
    time_of_robot_save = []
    time_of_human_save = []
    time_human_robot_diff = []
    start_time = None

    def __init__(self, nao_info):
        self.axes_len = None
        self.axes = None
        self.start_time = time.time()
        self.nao_info = nao_info

    def set_start_time(self):
        self.start_time = time.time()

    def traking_time_huan_robot_diff(self, times):
        self.time_human_robot_diff.append(times)

    def traking_human_joint(self, parts, joints_data):
        self.time_of_human_save.append(time.time() - self.start_time)
        joints = {}
        for i in range(len(parts)):
            joints[parts[i]] = joints_data[i]
        self.human_joints_save_of_time.append(joints)

    def traking_robot_joint(self, parts, joints_data):

        self.time_of_robot_save.append(time.time() - self.start_time)
        joints = {}
        for i in range(len(parts)):
            joints[parts[i]] = joints_data[i]
        self.robot_joints_save_of_time.append(joints)

    def make_graph(self, time_of_save, joints_save_of_time, start=0, end=0):
        graph_joint_time = {}
        for i in range(start, len(time_of_save)-end):
            times = time_of_save[i]
            for joint_name in joints_save_of_time[i].keys():
                joint = joints_save_of_time[i][joint_name]
                if joint < self.nao_info.min_angle[joint_name]:
                    joint = self.nao_info.min_angle[joint_name]
                elif joint > self.nao_info.max_angle[joint_name]:
                    joint = self.nao_info.max_angle[joint_name]
                if graph_joint_time.get(joint_name) is None:
                    graph_joint_time[joint_name] = [[times], [joint * almath.TO_DEG]]
                else:
                    graph_joint_time[joint_name][0].append(times)
                    graph_joint_time[joint_name][1].append(joint * almath.TO_DEG)
        return graph_joint_time

    def show_joints(self, graph_joint_time, color, sx=0, sy=0, plabel="", xlabel='time', ylabel='joint'):
        x = sx
        y = sy

        for key in graph_joint_time.keys():
            self.axes[y, x].plot(graph_joint_time[key][0], graph_joint_time[key][1], color + '-',
                                 markersize=2, label=plabel)
            self.axes[y, x].set_title(key)
            self.axes[y, x].set_xlabel(xlabel, fontsize=11)
            self.axes[y, x].set_ylabel(ylabel, fontsize=11)
            self.axes[y, x].legend(fontsize=7)
            x += 1
            if x >= self.axes_len:
                x = 0
                y += 1
        return x, y

    def get_graph_result(self, graph_joint_time_human, graph_joint_time_robot):
        graph_diff = {}

        roll_sum = 0
        roll_count = 0
        for key in graph_joint_time_human.keys():
            count = 0
            sums = 0
            graph_diff[key] = [graph_joint_time_human[key][0], []]
            for i in range(len(graph_joint_time_human[key][0])):
                diff = abs(graph_joint_time_human[key][1][i] - graph_joint_time_robot[key][1][i])
                robot_diff = max(abs(self.nao_info.max_angle[key]*almath.TO_DEG - graph_joint_time_robot[key][1][i]),
                                 abs(self.nao_info.min_angle[key]*almath.TO_DEG - graph_joint_time_robot[key][1][i]))
                graph_diff[key][1].append(1-diff/robot_diff)
                sums += 1-diff/robot_diff
                count += 1

            if 'Roll' in key:
                print(key + "diff mean : " + str(sums / count))
                roll_count += 1
                roll_sum += sums / count

        return [graph_diff, roll_sum, roll_count]

    @staticmethod
    def match_graph_bases(dict_graph, dict_graph2):

        for key in dict_graph.keys():
            print(key)
            print(dict_graph2[key][0][0], dict_graph[key][0][0])
            print(dict_graph2[key][1][0], dict_graph[key][1][0])
            diff_base_x = dict_graph2[key][0][0] - dict_graph[key][0][0]
            diff_base_y = dict_graph2[key][1][0] - dict_graph[key][1][0]
            print(diff_base_x, diff_base_y)
            for i in range(len(dict_graph2[key][0])):
                dict_graph2[key][0][i] -= diff_base_x
                dict_graph2[key][1][i] -= diff_base_y

        return dict_graph, dict_graph2

    @staticmethod
    def match_time(time_list, time_list2):

        for i in range(len(time_list)):
            diff = time_list2[i] - time_list[i]
            time_list2[i] -= diff

        return time_list, time_list2

    def show(self):
        graph_joint_time_human = self.make_graph(self.time_of_human_save, self.human_joints_save_of_time, 20, 10)
        graph_joint_time_robot = self.make_graph(self.time_of_robot_save, self.robot_joints_save_of_time, 20, 10)

        graph_joint_time_human, graph_joint_time_robot = self.match_graph_bases(graph_joint_time_human, graph_joint_time_robot)

        self.axes_len = int(math.sqrt(len(graph_joint_time_human))) + 2
        f, self.axes = plt.subplots(self.axes_len, self.axes_len)
        f.set_size_inches((5 * self.axes_len, 5 * self.axes_len))
        plt.subplots_adjust(wspace=0.2 * self.axes_len, hspace=0.2 * self.axes_len)

        graph_diff, roll_sum, roll_count = self.get_graph_result(graph_joint_time_human, graph_joint_time_robot)

        print("All Roll diff mean: " + str(roll_sum / roll_count))
        self.show_joints(graph_joint_time_human, 'b', plabel="humam_part_angle")
        x, y = self.show_joints(graph_joint_time_robot, 'r', plabel="robot_part_angle")

        # diff graph
        self.show_joints(graph_diff, 'g', x, y, plabel="human_and_robot_diff", ylabel='accuracy')

        print("human_min" + str(self.time_of_human_save))
        print("time_min" + str(self.time_of_robot_save))
        print("human_max" + str(self.time_of_human_save))
        print("time_max" + str(self.time_of_robot_save))

        plt.show()

        print(self.start_time)
        print(self.time_of_human_save)
