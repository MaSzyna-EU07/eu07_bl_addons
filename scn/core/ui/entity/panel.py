import bpy

from . import track
from . import model
from . import lines
from . import triangles
from . import traction

class SCN_PT_entity(bpy.types.Panel):
    bl_idname = "SCN_PT_entity"
    bl_label = "SCN Entity"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "[EU07] Developer Tools"

    @classmethod
    def poll(cls, context):
        return context.object and context.scene.eu07_project_properties.operating_mode == "scenery_editor"

    def draw(self, context):
        obj = context.object

        if not obj:
            return

        row = self.layout.row()
        row.prop(obj, "eu07_scn_entity_type")

        if obj.eu07_scn_entity_type == "node:track":
            track.draw(context, self.layout)
        elif obj.eu07_scn_entity_type == "node:model":
            model.draw(context, self.layout)
        elif obj.eu07_scn_entity_type == "node:lines":
            lines.draw(context, self.layout)
        elif obj.eu07_scn_entity_type == "node:triangles":
            triangles.draw(context, self.layout)
        elif obj.eu07_scn_entity_type == "node:traction":
            traction.draw(context, self.layout)