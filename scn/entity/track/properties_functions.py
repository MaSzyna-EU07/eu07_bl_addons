import bpy

from scn.entity.track import validate


# TODO: Create validators for entities to avoid long if if if
def get_length(self):
    obj = bpy.context.object
    if validate.is_curve(obj):
        return 0


def get_p1(self):
    return get_pX(1)


def set_p1(self, value):
    set_pX(1, value)


def get_p2(self):
    return get_pX(2)


def set_p2(self, value):
    set_pX(2, value)


def get_p3(self):
    return get_pX(3)


def set_p3(self, value):
    set_pX(3, value)


def get_p4(self):
    return get_pX(4)


def set_p4(self, value):
    set_pX(4, value)


def get_pX(x):
    spline_idx, point_idx = get_spline_and_point_indices(x)

    obj = bpy.context.object

    if validate.is_curve(obj):
        return obj.data.splines[spline_idx].bezier_points[point_idx].co

    return 0, 0, 0


def set_pX(x, value):
    spline_idx, point_idx = get_spline_and_point_indices(x)

    obj = bpy.context.object

    if validate.is_curve(obj):
        obj.data.splines[spline_idx].bezier_points[point_idx].co = value


def get_spline_and_point_indices(x):
    spline_idx = 0
    point_idx = x - 1

    if x > 2:
        spline_idx = 1
        point_idx = 4 - x

    return spline_idx, point_idx
