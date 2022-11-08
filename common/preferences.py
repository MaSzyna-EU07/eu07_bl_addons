import bpy
from bpy.props import StringProperty


def get_preferences():
    return bpy.context.preferences.addons['eu07_bl_addons'].preferences


class EU07AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = "eu07_bl_addons"

    default_environment_path: StringProperty(
        name="Default environment path",
        subtype='FILE_PATH'
    )

    trees_material_regex: StringProperty(
        name="Trees material filename filter",
        default="tree|drzewo|plant"
    )


classes = (
    EU07AddonPreferences,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
