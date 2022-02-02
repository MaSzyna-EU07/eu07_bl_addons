import math
import pathlib

from bpy_extras import view3d_utils
import bpy
import mathutils

import eu07_tools


def get_environment_path(fallback_path=""):
    env_path = bpy.context.scene.eu07_project_properties.environment_path
    if not env_path:
        if fallback_path:
            env_path = \
            bpy.context.scene.eu07_project_properties.environment_path = \
            eu07_tools.utils.find_asset_root(fallback_path)
        else:
            raise ValueError("EU07 Addon Error: Environment path not set")

    return env_path

def get_source_path(abspath):
    env_path = get_environment_path(abspath)
    return str(pathlib.Path(abspath).relative_to(env_path))

def uilist_safe_index_after_delete(uilist, index):
    return min(max(0, index - 1), len(uilist) - 1)


def get_viewport_camera_location():
    return view3d_utils.region_2d_to_origin_3d(bpy.context.region, bpy.context.space_data.region_3d, (0, 0))


def get_viewport_camera_rotation():
    region = bpy.context.space_data.region_3d

    direction = (region.view_location - get_viewport_camera_location()).normalized()

    roll = 0
    pitch = math.asin(direction.z)
    yaw = math.atan2(direction.y, direction.x)

    euler = mathutils.Euler((roll, pitch, yaw))

    return euler