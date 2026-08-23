import bpy
from bpy.props import StringProperty


def get_preferences():
    return bpy.context.preferences.addons[__package__].preferences


class EU07AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__


classes = (
    EU07AddonPreferences,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
