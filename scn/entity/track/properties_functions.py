import bpy

from scn.entity.track import validate
from scn.geometry.track import TrackNormalGeometryManager


def update_geometry(self, context):
    mngr = TrackNormalGeometryManager()
    geometry = mngr.get(self.id_data)
    mngr.set(self.id_data, geometry)

def get_length(self):
    obj = self.id_data
    if validate.is_curve(obj):
        return obj.data.splines[0].calc_length()

    return 0


def get_p1(self):
    obj = self.id_data
    return get_pX(obj, 1)


def set_p1(self, value):
    obj = self.id_data
    set_pX(obj, 1, value)


def get_p2(self):
    obj = self.id_data
    return get_pX(obj, 2)


def set_p2(self, value):
    obj = self.id_data
    set_pX(obj, 2, value)


def get_p3(self):
    obj = self.id_data
    return get_pX(obj, 3)


def set_p3(self, value):
    obj = self.id_data
    set_pX(obj, 3, value)


def get_p4(self):
    obj = self.id_data
    return get_pX(obj, 4)


def set_p4(self, value):
    obj = self.id_data
    set_pX(obj, 4, value)


def get_cv1(self):
    obj = self.id_data
    return get_cvX(obj, 1)


def set_cv1(self, value):
    obj = self.id_data
    return set_cvX(obj, 1, value)


def get_cv2(self):
    obj = self.id_data
    return get_cvX(obj, 2)


def set_cv2(self, value):
    obj = self.id_data
    return set_cvX(obj, 2, value)


def get_cv3(self):
    obj = self.id_data
    return get_cvX(obj, 3)


def set_cv3(self, value):
    obj = self.id_data
    return set_cvX(obj, 3, value)


def get_cv4(self):
    obj = self.id_data
    return get_cvX(obj, 4)


def set_cv4(self, value):
    obj = self.id_data
    return set_cvX(obj, 4, value)


def get_pX(obj, x):
    spline_idx, point_idx = get_spline_and_point_indices(x)

    if validate.is_curve(obj):
        return obj.data.splines[spline_idx].bezier_points[point_idx].co

    return 0, 0, 0


def set_pX(obj, x, value):
    spline_idx, point_idx = get_spline_and_point_indices(x)


    if validate.is_curve(obj):
        point = obj.data.splines[spline_idx].bezier_points[point_idx]
        point.co = value

        point.handle_left_type = 'FREE'
        point.handle_right_type = 'FREE'


def get_spline_and_point_indices(x):
    spline_idx = 0
    point_idx = x - 1

    if x > 2:
        spline_idx = 1
        point_idx = 4 - x

    return spline_idx, point_idx


def get_cvX(obj, x):
    spline_idx, point_idx = get_spline_and_point_indices(x)

    if validate.is_curve(obj):
        point = obj.data.splines[spline_idx].bezier_points[point_idx]

        # TODO: Relative to pX
        if x % 2 == 0:
            return point.handle_left
        else:
            return point.handle_right


def set_cvX(obj, x, value):
    spline_idx, point_idx = get_spline_and_point_indices(x)

    if validate.is_curve(obj):
        point = obj.data.splines[spline_idx].bezier_points[point_idx]
        # TODO: Relative to pX
        if x % 2 == 0:
            point.handle_left = value
            point.handle_right = 0, 0, 0
            point.handle_left_type = 'FREE'
        else:
            point.handle_right = value
            point.handle_left = 0, 0, 0
            point.handle_right_type = 'FREE'