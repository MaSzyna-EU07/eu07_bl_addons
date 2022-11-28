import bpy

class EU07_PT_ProjectProperties(bpy.types.Panel):
    bl_idname = "EU07_PT_ProjectProperties"
    bl_label = "[EU07] Project Properties"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_category = "[EU07] Developer Tools"

    def draw(self, context):
        project_properties = context.scene.eu07_project_properties

        self.layout.prop(project_properties, "operating_mode")
        self.layout.prop(project_properties, "environment_path")


def register():
    bpy.utils.register_class(EU07_PT_ProjectProperties)


def unregister():
    bpy.utils.unregister_class(EU07_PT_ProjectProperties)