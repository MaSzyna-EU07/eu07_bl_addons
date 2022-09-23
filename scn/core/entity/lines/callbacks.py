
def get_thickness(self):
    obj = self.id_data
    return obj.data.bevel_depth


def set_thickness(self, thickness):
    obj = self.id_data
    obj.data.bevel_mode = 'ROUND'
    obj.data.bevel_resolution = 0
    obj.data.bevel_depth = thickness
