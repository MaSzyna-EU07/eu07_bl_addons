import math

import bpy
import mathutils
import eu07_tools


def create_camera_from_element(element):
    camera_datablock = bpy.data.cameras.new(f"Camera {element.index}")
    camera_object = bpy.data.objects.new(f"Camera {element.index}", camera_datablock)

    camera_object.location = element.location.swizzled()
    camera_object.rotation_euler = mathutils.Euler(
        [
            math.radians(element.rotation.x),
            math.radians(element.rotation.y),
            math.radians(element.rotation.z)
        ],
        'XYZ'
    )

    # by default, camera points to south, so we need additional rotations there
    # because blender's camera points to the bottom by default
    camera_object.rotation_euler.rotate_axis('Z', math.radians(180))
    camera_object.rotation_euler.rotate_axis('X', math.radians(90))

    bpy.context.scene.collection.objects.link(camera_object)


def create_element_from_camera(camera):
    element = eu07_tools.scn.create_element("camera")

    return element