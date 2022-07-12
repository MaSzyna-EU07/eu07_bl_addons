
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

def get_pX(obj, x):
    spline_idx, point_idx = get_spline_and_point_indices(x)

    return obj.matrix_world @ obj.data.splines[spline_idx].bezier_points[point_idx].co

def set_pX(obj, x, value):
    spline_idx, point_idx = get_spline_and_point_indices(x)

    point = obj.data.splines[spline_idx].bezier_points[point_idx]
    point.co = value

    point.handle_left_type = 'VECTOR'
    point.handle_right_type = 'VECTOR'


def get_spline_and_point_indices(x):
    spline_idx = 0
    point_idx = x - 1

    if x > 2:
        spline_idx = 1
        point_idx = 4 - x

    return spline_idx, point_idx