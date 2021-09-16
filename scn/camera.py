import math
import copy

import bpy
import mathutils
import eu07_tools

from scn.sectorizer import Sectorizer


def create_camera_from_element(element):
    camera_datablock = bpy.data.cameras.new(f"Camera {element.index}")
    camera_object = bpy.data.objects.new(f"Camera {element.index}", camera_datablock)
    camera_object.scn_properties.type_ = "camera"

    if element.index != -1:
        camera_object.scn_properties.camera_use_index = True
        camera_object.scn_properties.camera_index = element.index

    camera_object.location = element.location.swizzled()
    camera_object.rotation_euler = mathutils.Euler(
        [
            math.radians(element.rotation.x),
            math.radians(element.rotation.z),
            math.radians(element.rotation.y)
        ],
        'XYZ'
    )

    # by default, camera points to south, so we need additional rotations there
    # because blender's camera points to the bottom by default
    camera_object.rotation_euler = compensate_camera_angles(camera_object.rotation_euler.copy())

    collection = bpy.data.collections.get("Cameras", bpy.data.collections.new("Cameras"))
    collection.objects.link(camera_object)

    Sectorizer.auto_put(camera_object)


def create_element_from_camera(camera_object):
    element = eu07_tools.scn.create_element("camera")

    element.location = eu07_tools.utils.swizzle_coords(camera_object.location)
    element.rotation = eu07_tools.utils.swizzle_coords(
        [math.degrees(x) for x in compensate_camera_angles(camera_object.rotation_euler.copy(), factor=-1)]
    )

    if camera_object.scn_properties.camera_use_index:
        element.index = camera_object.scn_properties.camera_index

    return element


def get_cameras_with_index(index):
    users = []

    for obj in bpy.data.collections["Cameras"].objects:
        if obj.scn_properties.type_ == 'camera':
            if obj.scn_properties.camera_use_index:
                if obj.scn_properties.camera_index == index:
                    users.append(obj)

    return users


def compensate_camera_angles(euler, factor=1):
    if factor == -1:
        euler.rotate_axis('X', math.radians(90 * factor))
        euler.rotate_axis('Z', math.radians(180 * factor))
    else:
        euler.rotate_axis('Z', math.radians(180 * factor))
        euler.rotate_axis('X', math.radians(90 * factor))

    return euler
