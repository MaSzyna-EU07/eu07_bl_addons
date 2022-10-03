import bpy
import eu07_tools

from . import randomtextureset as randomtextureset_mod

NODEGROUP_NAME = "[EU07] Material Block"
VARIANT_NAMES = [
    "Spring",
    "Summer",
    "Autumn",
    "Winter",
    "Clear",
    "Cloudy",
    "Rain",
    "Snow"
]
MAX_TEXTURES_NUM = 8

class EU07_MATShaderParam(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    value_string: bpy.props.StringProperty()

    @property
    def values_list(self):
        stripped = self.value_string.strip()
        if stripped:
            if " " in stripped:
                return [float(x) for x in stripped.split(" ")]
            else:
                return [float(stripped)]

        return []


class EU07_MATBlock(bpy.types.PropertyGroup):
    shader_name: bpy.props.StringProperty(
        name="Shader Name",
        description="Name of shader to be used",
    )
    shader_params: bpy.props.CollectionProperty(
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

    opacity: bpy.props.IntProperty(
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
            if node.bl_idname == "ShaderNodeGroup" and node.name == randomtextureset_mod.RANDOM_TEXTURESET_NAME:
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

    def set_shader_param_value(self, name, value):
        param = self._get_shader_param(name)
        if not param:
            param = self.shader_params.add()
            param.name = name
        param.value_string = " ".join(str(x) for x in value)

    def get_shader_param_value(self, name):
        param = self._get_shader_param(name)
        return param.values_list

    def _get_shader_param(self, name):
        for shader_param in self.shader_params:
            if shader_param.name == name:
                return shader_param

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

        for variant_name in VARIANT_NAMES:
            ng.inputs.new("NodeSocketShader", variant_name)

    return ng


class EU07_UL_MATShaderParams(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'KEYFRAME'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.prop(item, "name", text="")
            row.prop(item, "value_string", text="")

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon=custom_icon)


classes = (
    EU07_MATShaderParam,
    EU07_MATBlock,
    EU07_UL_MATShaderParams,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.ShaderNodeGroup.eu07_matblock = bpy.props.PointerProperty(type=EU07_MATBlock)
    bpy.types.ShaderNodeGroup.eu07_active_shader_param_index = bpy.props.IntProperty()


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.ShaderNodeGroup.eu07_matblock
    del bpy.types.ShaderNodeGroup.eu07_active_shader_param_index