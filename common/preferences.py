import bpy
from bpy.props import StringProperty


def get_preferences():
    return bpy.context.preferences.addons['eu07_bl_addons'].preferences


class EU07AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = "eu07_bl_addons"

    root: StringProperty(
        name="Root path",
        subtype='FILE_PATH'
    )

    trees_material_regex: StringProperty(
        name="Trees material name filter",
        default="tree|drzewo|plant"
    )

    executable: bpy.props.StringProperty(
        name="Preview Executable",
        default="eu07.exe",
    )

    def draw(self, context):
        self.layout.prop(self, "root")
        self.layout.prop(self, "trees_material_regex")


classes = (
    EU07AddonPreferences,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
