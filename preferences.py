import bpy
from bpy.props import StringProperty


class EU07AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    root: StringProperty(
        name="Root path",
        subtype='FILE_PATH'
    )

    def draw(self, context):
        self.layout.prop(self, "root")


def register():
    bpy.utils.register_class(EU07AddonPreferences)


def unregister():
    bpy.utils.unregister_class(EU07AddonPreferences)
