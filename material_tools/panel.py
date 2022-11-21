import bpy

from material_tools.structures import matblock as matblock_mod
from material_tools.utils import get_active_material, get_active_material_node


class EU07_PT_MaterialToolsPanel(bpy.types.Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "[EU07] Tools"
    bl_label = "[EU07] Material Tools"

    def draw(self, context):
        active_bl_material = context.view_layer.objects.active.active_material
        eu07_material = active_bl_material.eu07_material if active_bl_material else None

        if eu07_material:
            if eu07_material.is_mat:
                row = self.layout.row()
                row.prop(eu07_material, "mat_source_path")

        import_op = self.layout.operator("eu07.import_material", text="Import Material as New", icon="PLUS")
        import_op.import_into_active = False
        import_op.set_new_as_active = True

        row = self.layout.row()
        row.enabled = (eu07_material is not None)
        import_op_repl = row.operator("eu07.import_material", text="Import Material to Active", icon="IMPORT")
        import_op_repl.import_into_active = True

        row = self.layout.row()
        export_op_as = row.operator("eu07.export_material", text="Export Material As...", icon="EXPORT")
        row.enabled = eu07_material is not None and eu07_material.is_mat

        self.layout.operator("eu07.broadcast_skin", text="Broadcast Skin", icon="PARTICLES")

        box = self.layout.box()
        box.label(text="MAT Nodes Manager", icon="NODETREE")
        box.operator("eu07.provide_mat_nodegroups", icon="IMPORT")
        box.operator("eu07.remove_mat_nodegroups", icon="TRASH")


class EU07_PT_MATEntityProperties(bpy.types.Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "[EU07] Tools"
    bl_label = "MAT Entity Properties"

    @classmethod
    def poll(cls, context):
        active_object = context.view_layer.objects.active
        if active_object:
            active_material = active_object.active_material
            return active_material and active_material.eu07_material.is_mat

        return False

    def draw(self, context):
        active_bl_material = get_active_material(context)
        active_node = get_active_material_node(active_bl_material)
        if not active_node:
            return

        if active_node.bl_idname == "ShaderNodeTexImage":
            eu07_tex = active_node.eu07_texture
            self.layout.prop(eu07_tex, "placeholder_path")
            b = self.layout.box()
            b.label(text="Traits")
            b.prop(eu07_tex, "disable_wrap_s")
            b.prop(eu07_tex, "disable_wrap_t")
            b.prop(eu07_tex, "use_sharpen")
        elif active_node.bl_idname == "ShaderNodeGroup":
            self.layout.label(text="Shader Node Group Inputs:")
            row = self.layout.row()

            disable_op = row.operator("eu07.toggle_shader_inputs", text="Disable All")
            disable_op.hidden_state = True

            enable_op = row.operator("eu07.toggle_shader_inputs", text="Enable All")
            enable_op.hidden_state = False

            for inp in active_node.inputs:
                row = self.layout.row()
                row.prop(inp, "hide", text=inp.name, toggle=1, invert_checkbox=True)


classes = (
    EU07_PT_MaterialToolsPanel,
    EU07_PT_MATEntityProperties,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)