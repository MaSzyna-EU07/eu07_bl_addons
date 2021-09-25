import bpy
from bpy.props import StringProperty

def get_preferences():
    return bpy.context.preferences.addons['eu07_bl_addons'].preferences


class EU07AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    root: StringProperty(
        name="Root path",
        subtype='FILE_PATH'
    )

    trees_material_regex: StringProperty(
        name="Trees material name filter",
        default="tree|drzewo|plant"
    )

    def draw(self, context):
        self.layout.prop(self, "root")
        self.layout.prop(self, "trees_material_regex")



def register():
    bpy.utils.register_class(EU07AddonPreferences)


def unregister():
    bpy.utils.unregister_class(EU07AddonPreferences)
