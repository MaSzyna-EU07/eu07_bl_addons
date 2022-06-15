import bpy

from . import common
from . import model
from . import scenery

class EU07_PT_GameEnginePreview(bpy.types.Panel):
    bl_idname = "EU07_PT_GameEnginePreview"
    bl_label = "View In Engine"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "[EU07] Developer Tools"

    def draw(self, context):
        operating_mode = bpy.context.scene.eu07_project_properties.operating_mode
        if operating_mode == "modelling":
            model.ui.draw(self, context)
        elif operating_mode == "scenery_editor":
            scenery.ui.draw(self, context)



def register():
    bpy.utils.register_class(EU07_PT_GameEnginePreview)
    model.register()
    scenery.register()


def unregister():
    bpy.utils.unregister_class(EU07_PT_GameEnginePreview)
    model.unregister()
    scenery.unregister()