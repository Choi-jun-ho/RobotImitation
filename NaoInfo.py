
class NaoInfo(object):

    min_angle = {}
    max_angle = {}
    max_velocity = {}
    max_torque = {}

    def __init__(self, motion_service, parts=None):

        if parts is None:
            parts = motion_service.getBodyNames("Body")

        for part in parts:
            limits = motion_service.getLimits(part)[0]
            self.min_angle[part] = limits[0]
            self.max_angle[part] = limits[1]
            self.max_velocity[part] = limits[2]
            self.max_torque[part] = limits[3]
