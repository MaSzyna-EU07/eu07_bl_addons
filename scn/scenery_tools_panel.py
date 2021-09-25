import bpy


class SCNToolsPanel(bpy.types.Panel):
    bl_idname = "SCENE_PT_scn"
    bl_label = "Scenery Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "[EU07] SCN Editor"

    def draw(self, context):
        add_tree_row = self.layout.row()
        add_tree_row.operator('eu07.add_tree')