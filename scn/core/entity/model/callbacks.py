import math
import pathlib

import mathutils

import bpy

import eu07_tools


def update_geometry(self, context):
    obj = self.id_data

    model_geo = context.scene.eu07_scn_model_bank.get_by_relpath(obj.eu07_scn_model.model_path, load_if_missing=True)
    if model_geo:
        obj.data = model_geo.mesh
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

