import bpy
import enum


# Opacity flag is used in Material Node Trees. It's needed for alpha clipping algorithm.


def callback_get_flag(self):
    obj = self.id_data
    # TODO: Support for scenery objects

    if obj.active_material:
        return obj.active_material.eu07_material.get_opacity_flag()

    return 1


def register():
    bpy.types.Object.eu07_opacity_flag = bpy.props.IntProperty(
        name="EU07 Opacity Flag",
        description="Opacity flag for this object (readonly). 0 - alpha blend, 1 - opaque (clip 0.5)",
        get=callback_get_flag,
    )


def unregister():
    del bpy.types.Object.eu07_opacity_flag