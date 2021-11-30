import math

from bpy_extras import view3d_utils
import bpy
import mathutils

import eu07_tools

from common import preferences

def get_root(abspath=""):
    try:
        root = eu07_tools.utils.find_asset_root(abspath)
    except ValueError:
        root = preferences.get_preferences().root
        if not root:
            raise ValueError(f"Can't find root path for {abspath}")

    return root


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