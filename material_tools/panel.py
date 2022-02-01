import bpy


class EU07_PT_MaterialToolsPanel(bpy.types.Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "[EU07] Tools"
    bl_label = "[EU07] Material Tools"

    @classmethod
    def poll(cls, context):
        return context.view_layer.objects.active.active_material is not None

    def draw(self, context):
        active_material = context.view_layer.objects.active.active_material

        source_row = self.layout.row()
        source_row.prop(active_material.eu07_properties, "source_path")
        source_row.enabled = False

        import_op = self.layout.operator("eu07.import_material", text="New Material", icon="PLUS")
        import_op.import_into_active = False
        import_op.set_new_as_active = True

        import_op_repl = self.layout.operator("eu07.import_material", text="Replace Material", icon="OVERLAY")
        import_op_repl.import_into_active = True

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