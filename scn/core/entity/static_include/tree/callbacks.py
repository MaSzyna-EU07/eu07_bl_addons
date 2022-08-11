import math


def get_location(self):
    return self.id_data.location


def set_location(self, location):
    self.id_data.location = location


# TODO: Make it rotate good
def get_rotation(self):
    fac = 180 / math.pi
    return mathutils.Vector(self.id_data.rotation_euler) * fac


def set_rotation(self, value):
    self.id_data.rotation_euler = mathutils.Euler(
        [math.radians(v) for v in value]
    )


def get_height(self):
    return self.id_data.scale.z


def set_height(self, height):
    self.id_data.scale.z = height


def get_span(self):
    return self.id_data.scale.x / 2


def set_span(self, span):
    self.id_data.scale.x = span * 2
    self.id_data.scale.y = span * 2

