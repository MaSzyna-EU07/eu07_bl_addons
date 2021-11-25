import bpy


class EU07_PT_MaterialToolsPanel(bpy.types.Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "[EU07] Tools"
    bl_label = "[EU07] Material Tools"

    def draw(self, context):
        self.layout.operator("eu07.import_material", text="Import To New Material", icon="IMPORT")
        import_op = self.layout.operator("eu07.import_material", text="Import To Active Material", icon="IMPORT")
        import_op.import_into_active = True