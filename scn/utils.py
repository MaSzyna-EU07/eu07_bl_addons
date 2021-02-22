import math

import bpy

from ..common import create_material_from_path


def set_trajectory_profile(trajectory, new_profile_object):
    old_profile = get_trajectory_profile(trajectory)

    if (old_profile is not None):
        bpy.data.objects.remove(old_profile)

    new_profile_object.parent = trajectory
    new_profile_object.location = (0, 0, 0)
    new_profile_object.hide_select = True
    # trajectory.users_collection[0].objects.link(new_profile_object)
    new_profile_object.modifiers["Array"].curve = trajectory
    new_profile_object.modifiers["Curve"].object = trajectory


def get_trajectory_profile(trajectory):
    try:
        return next((c for c in trajectory.children if c.name.startswith("TProfile")))
    except StopIteration:
        return None


def set_trajectory_material(trajectory, material, index):
    profile_object = get_trajectory_profile(trajectory)
    profile_object.material_slots[index].material = material


def get_trajectory_material(trajectory, index):
    profile_object = get_trajectory_profile(trajectory)
    return profile_object.material_slots[index].material


def load_trajectory_materials(map_names, asset_searcher):
    materials = []

    for i, map_name in enumerate(map_names):
        materials.append(create_material_from_path(asset_searcher.textures.find(map_name)))

    return materials


## SECTOR UTILS

