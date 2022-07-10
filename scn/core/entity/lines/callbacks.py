from material_tools.wrapper import MaterialWrapper


def get_thickness(self):
    obj = self.id_data
    return obj.data.bevel_depth


def set_thickness(self, thickness):
    obj = self.id_data
    obj.data.bevel_mode = 'ROUND'
    obj.data.bevel_resolution = 0
    obj.data.bevel_depth = thickness


def get_color(self):
    obj = self.id_data
    if not obj.active_material:
        obj.active_material = obj.data.materials.new()

    wrapper = MaterialWrapper(obj.active_material)
    return wrapper.get_diffuse_color()


def set_color(self, color):
    obj = self.id_data
    if not obj.active_material:
        obj.active_material = obj.data.materials.new()

    wrapper = MaterialWrapper(obj.active_material)
    return wrapper.set_diffuse_color(color[:3])