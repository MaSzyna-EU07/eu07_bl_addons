import bpy


class EU07_PT_MaterialToolsPanel(bpy.types.Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "[EU07] Tools"
    bl_label = "[EU07] Material Tools"

    def draw(self, context):
        active_bl_material = context.view_layer.objects.active.active_material
        eu07_material = active_bl_material.eu07_material if active_bl_material else None


        if eu07_material:
            is_imported_row = self.layout.row()
            is_imported_row.prop(eu07_material, "is_mat")

            if eu07_material.is_mat:
                row = self.layout.row()
                row.prop(eu07_material, "mat_source_path")


        import_op = self.layout.operator("eu07.import_material", text="New Material", icon="PLUS")
        import_op.import_into_active = False
        import_op.set_new_as_active = True

        row = self.layout.row()
        import_op_repl = row.operator("eu07.import_material", text="Replace Material", icon="OVERLAY")
        import_op_repl.import_into_active = True
        row.enabled = (eu07_material is not None)

        self.layout.operator("eu07.broadcast_skin", text="Broadcast Skin", icon="PARTICLES")


classes = (
    EU07_PT_MaterialToolsPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)