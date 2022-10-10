class MotionData(object):
    def __init__(self):
        self.parts_name = []
        self.angles = []
        self.speeds = []
        self.times = []

    def add(self, motion_data):
        if motion_data is not None:
            self.parts_name.extend(motion_data.parts_name)
            self.angles.extend(motion_data.angles)
            self.speeds.extend(motion_data.speeds)
            self.times.extend(motion_data.times)

