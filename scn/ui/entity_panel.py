import bpy


class SCN_PT_entity(bpy.types.Panel):
    bl_idname = "SCN_PT_entity"
    bl_label = "SCN Entity"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "[EU07] Developer Tools"

    @classmethod
    def poll(cls, context):
        return context.scene.eu07_project_properties.operating_mode == "scenery_editor"

    def draw(self, context):
        self.obj = context.object

        type_r = self.layout.label(text="dupa")