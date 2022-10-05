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
            is_imported_row = self.layout.row()
            is_imported_row.prop(eu07_material, "is_mat")

            if eu07_material.is_mat:
                row = self.layout.row()
                row.prop(eu07_material, "mat_source_path")


        import_op = self.layout.operator("eu07.import_material", text="New Material", icon="PLUS")
        import_op.import_into_active = False
        import_op.set_new_as_active = True

        row = self.layout.row()
        import_op_repl = row.operator("eu07.import_material", text="Import Material", icon="IMPORT")
        import_op_repl.import_into_active = True
        row.enabled = (eu07_material is not None)
        
        row = self.layout.row()
        export_op_repl = row.operator("eu07.export_material", text="Export Material", icon="EXPORT")
        row.enabled = (eu07_material is not None)

        self.layout.operator("eu07.broadcast_skin", text="Broadcast Skin", icon="PARTICLES")


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
            self.layout.prop(active_node.eu07_texture, "mat_alias")
        elif matblock_mod.poll_helper(context):
            matblock_data = active_node.eu07_matblock
            self.layout.prop(matblock_data, "shader_name")
            sbox = self.layout.box()
            sbox.label(text="Shader Parameters:")
            sbox.template_list(
                "EU07_UL_MATShaderParams", "",
                matblock_data, "shader_params_internal",
                matblock_data, "active_shader_param_index"
            )
            row = sbox.row()
            row.operator("eu07.mat_add_shader_param", text="Add")
            row.operator("eu07.mat_remove_shader_param", text="Remove")
            active_param = matblock_data.get_active_shader_param()
            sbox.prop(active_param, "name", text="Name")
            sbox.prop(active_param, "value_string", text="Values")
            self.layout.prop(matblock_data, "shadow_rank")
            self.layout.prop(matblock_data, "size")
            self.layout.prop(matblock_data, "opacity")
            self.layout.prop(matblock_data, "selfillum")


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