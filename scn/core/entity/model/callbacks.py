import math
import pathlib

import mathutils

import bpy

from ..... import eu07_tools


def update_geometry(self, context):
    obj = self.id_data

    model_geo = context.scene.eu07_scn_model_bank.get_by_relpath(obj.eu07_scn_model.model_path, load_if_missing=True)
    if model_geo:
        obj.data = model_geo.mesh

        # Reset previous model's slot settings
        for material_slot in obj.material_slots:
            material_slot.link = 'DATA'

        skin_mat_indices = [skin.material_index for skin in obj.data.eu07_scn_model_skins]

        for material_slot in obj.material_slots:
            if material_slot.slot_index in skin_mat_indices:
                material_slot.link = 'OBJECT'

        #TODO: Update replacableskin_1 etc with materials from slots in order to refresh field value when changing model
    else:
        obj.data = bpy.data.meshes.get("EmptyMesh", bpy.data.meshes.new("EmptyMesh"))


def update_path(self, context):
    obj = self.id_data

    path = pathlib.Path(obj.eu07_scn_model.model_path).with_suffix("")
    if path.is_absolute():
        obj.eu07_scn_model.model_path = eu07_tools.utils.shorten_asset_path(path)
        return

    update_geometry(self, context)


def get_location(self):
    return self.id_data.location


def set_location(self, value):
    self.id_data.location = value


# TODO: Make it rotate good
def get_rotation(self):
    fac = 180 / math.pi
    return mathutils.Vector(self.id_data.rotation_euler) * fac


def set_rotation(self, value):
    self.id_data.rotation_euler = mathutils.Euler(
        [math.radians(v) for v in value]
    )


def update_replacableskin_1(self, context):
    obj = self.id_data
    update_replacableskin_x(obj, obj.eu07_scn_model.replacableskin_1, -1)


def update_replacableskin_2(self, context):
    obj = self.id_data
    update_replacableskin_x(obj, obj.eu07_scn_model.replacableskin_2, -2)


def update_replacableskin_3(self, context):
    obj = self.id_data
    update_replacableskin_x(obj, obj.eu07_scn_model.replacableskin_3, -3)


def update_replacableskin_4(self, context):
    obj = self.id_data
    update_replacableskin_x(obj, obj.eu07_scn_model.replacableskin_4, -4)


def update_replacableskin_x(obj, material, skin_id):
    for skin_data in obj.data.eu07_scn_model_skins:
        if skin_data.skin_id == skin_id:
            obj.material_slots[skin_data.material_index].material = material

