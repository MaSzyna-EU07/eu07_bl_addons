import bpy
import eu07_tools
from common import uilist_safe_index_after_delete

from . import randomtextureset as randomtextureset_mod
from ..utils import get_active_material, get_active_material_node

NODEGROUP_NAME = "[EU07] Material Block"
MAX_TEXTURES_NUM = 8


class EU07_MATShaderParam(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    value_string: bpy.props.StringProperty()

    def get_values_list(self):
        stripped = self.value_string.strip()
        if stripped:
            if " " in stripped:
                return [float(x) for x in stripped.split(" ")]
            else:
                return [float(stripped)]

        return []

    def set_values_list(self, values):
        self.value_string = " ".join(str(x) for x in values)



class EU07_MATBlock(bpy.types.PropertyGroup):
    shader_name: bpy.props.StringProperty(
        name="Shader Name",
        description="Name of shader to be used",
    )
    active_shader_param_index: bpy.props.IntProperty()
    shader_params_internal: bpy.props.CollectionProperty(
        type=EU07_MATShaderParam,
    )
    shadow_rank: bpy.props.IntProperty(
        name="Shadow Rank",
        description="",
        default=3,
        max=3,
        min=1
    )

    size: bpy.props.FloatVectorProperty(
        name="Size",
        size=2,
        default=(-1, -1),
        min=-1,
    )

    opacity: bpy.props.FloatProperty(
        name="Opacity",
        default=1,
        min=0,
        max=1
    )

    selfillum: bpy.props.FloatProperty(
        name="SelfIllum",
        default=-1,
        min=-1,
        max=2
    )

    # HACK: self.id_data returns main node tree so i took this workaround from
    # https://blender.stackexchange.com/questions/214446/adding-properties-to-a-shader-node
    @property
    def bl_node(self):
        nodes = [n for n in self.id_data.nodes if n.type == 'GROUP']
        for n in nodes:
            n.eu07_matblock.name = n.name

        return self.id_data.nodes.get(self.name)

    @property
    def bl_node_tree(self):
        return self.id_data

    @property
    def is_valid(self):
        return self.bl_node.node_tree.name == NODEGROUP_NAME

    def set_to_texture_slot(self, entity, slot_name):
        self.bl_node_tree.links.new(
            entity.bl_node.outputs[0],
            self._get_texture_slot_input(slot_name)
        )

    def get_from_texture_slot(self, slot_name):
        input_ = self._get_texture_slot_input(slot_name)
        if input_.links:
            node = input_.links[0].from_node
            if node.bl_idname == "ShaderNodeGroup" and node.node_tree.name == randomtextureset_mod.RANDOM_TEXTURESET_NAME:
                return node.eu07_randomtextureset
            else:
                return node.eu07_texture

    def set_subblock(self, subblock, variant_name):
        self.bl_node_tree.links.new(
            subblock.bl_node.outputs[0],
            self._get_variant_input(variant_name)
        )

    def get_subblock(self, variant_name):
        input_ = self._get_variant_input(variant_name)
        if input_.links:
            return input_.links[0].from_node.eu07_matblock

    def get_active_shader_param(self):
        try:
            return self.shader_params_internal[self.active_shader_param_index]
        except IndexError:
            return None

    def add_shader_param(self):
        param = self.shader_params_internal.add()
        param.name = "param_X"
        param.set_values_list([0,])
        return param

    def get_shader_param(self, name):
        for param in self.shader_params_internal:
            if name == param.name:
                return param

    def remove_shader_param(self, rem_param):
        for i, param in enumerate(self.shader_params_internal):
            if param.name == rem_param.name:
                self.shader_params_internal.remove(i)
                self.active_shader_param_index = uilist_safe_index_after_delete(
                    self.shader_params_internal, self.active_shader_param_index
                )

    def iter_shader_params(self):
        for param in self.shader_params_internal:
            yield param

    def _get_texture_slot_input(self, slot_name):
        for input in self.bl_node.inputs:
            if input.name.lower() == slot_name.lower():
                return input

    def _get_variant_input(self, variant_name):
        for input_ in self.bl_node.inputs:
            if input_.name.lower() == variant_name.lower():
                return input_


def get_template():
    ng = bpy.data.node_groups.get(NODEGROUP_NAME)

    if ng is None:
        ng = bpy.data.node_groups.new(NODEGROUP_NAME, 'ShaderNodeTree')

        ng_output = ng.nodes.new("NodeGroupOutput")
        ng.outputs.new("NodeSocketShader", "Output")

        ng_input = ng.nodes.new("NodeGroupInput")

        for texture_index in range(1, MAX_TEXTURES_NUM + 1):
            texture_socket = ng.inputs.new("NodeSocketColor", f"Texture{texture_index}")

        for variant_name in eu07_tools.mat.NESTED_MAPPING_KEYS:
            ng.inputs.new("NodeSocketShader", variant_name.capitalize())

    return ng


class EU07_UL_MATShaderParams(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'KEYFRAME'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon=custom_icon)


def poll_helper(context):
    active_mat = get_active_material(context)
    active_node = get_active_material_node(active_mat)
    return active_node.bl_idname == "ShaderNodeGroup" and active_node.node_tree.name == NODEGROUP_NAME


class EU07_OT_MATAddShaderParam(bpy.types.Operator):
    bl_idname = "eu07.mat_add_shader_param"
    bl_label = "Add Shader Param"

    @classmethod
    def poll(cls, context):
        return poll_helper(context)

    def execute(self, context):
        material = get_active_material(context)
        node = get_active_material_node(material)

        param = node.eu07_matblock.add_shader_param()
        param.name = "param_X"
        param.set_values_list([0,])

        return {'FINISHED'}


class EU07_OT_MATRemoveShaderParam(bpy.types.Operator):
    bl_idname = "eu07.mat_remove_shader_param"
    bl_label = "Remove Shader Param"

    @classmethod
    def poll(cls, context):
        return poll_helper(context)

    def execute(self, context):
        material = get_active_material(context)
        node = get_active_material_node(material)

        active_param = node.eu07_matblock.get_active_shader_param()
        if active_param:
            node.eu07_matblock.remove_shader_param(active_param)

        return {'FINISHED'}


classes = (
    EU07_MATShaderParam,
    EU07_MATBlock,
    EU07_UL_MATShaderParams,
    EU07_OT_MATAddShaderParam,
    EU07_OT_MATRemoveShaderParam
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.ShaderNodeGroup.eu07_matblock = bpy.props.PointerProperty(type=EU07_MATBlock)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.ShaderNodeGroup.eu07_matblock