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

    preview_command: StringProperty(
        name="Preview CMD/Bash command",
        default="eu07.exe -s blender_export_preview.scn"
    )

    def draw(self, context):
        self.layout.prop(self, "root")
        self.layout.prop(self, "trees_material_regex")
        self.layout.prop(self, "preview_command")


classes = (
    EU07AddonPreferences,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
