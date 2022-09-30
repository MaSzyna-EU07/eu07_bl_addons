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

class EU07_MATBlock(bpy.types.PropertyGroup):
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

    @property
    def shader_name(self):
        return self.bl_node.inputs[0].default_value

    @shader_name.setter
    def shader_name(self, shader_name):
        self.bl_node.inputs[0].default_value = shader_name

    # TODO: Shader params
    @property
    def shader_params_string(self):
        return self.bl_node.inputs[1].default_value

    @shader_params_string.setter
    def shader_params_string(self, sps):
        self.bl_node.inputs[1].default_value = sps

    @property
    def shadow_rank(self):
        return self.bl_node.inputs[18].default_value

    @shadow_rank.setter
    def shadow_rank(self, shadow_rank):
        self.bl_node.inputs[18].default_value = shadow_rank

    @property
    def size_x(self):
        return self.bl_node.inputs[19].default_value

    @size_x.setter
    def size_x(self, size_x):
        self.bl_node.inputs[19].default_value = size_x

    @property
    def size_y(self):
        return self.bl_node.inputs[20].default_value

    @size_y.setter
    def size_y(self, size_y):
        self.bl_node.inputs[20].default_value = size_y

    @property
    def opacity(self):
        return self.bl_node.inputs[21].default_value

    @opacity.setter
    def opacity(self, opacity):
        self.bl_node.inputs[21].default_value = opacity

    @property
    def selfillum(self):
        return self.bl_node.inputs[22].default_value

    @selfillum.setter
    def selfillum(self, selfillum):
        self.bl_node.inputs[22].default_value = selfillum

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

        ng.inputs.new("NodeSocketString", "Shader File")
        ng.inputs.new("NodeSocketString", "Shader Params")

        for texture_index in range(1, MAX_TEXTURES_NUM + 1):
            texture_socket = ng.inputs.new("NodeSocketColor", f"Texture{texture_index}")

        for variant_name in VARIANT_NAMES:
            ng.inputs.new("NodeSocketShader", variant_name)

        shadow_rank_socket = ng.inputs.new("NodeSocketInt", "Shadow Rank")
        shadow_rank_socket.min_value = 1
        shadow_rank_socket.max_value = 3
        shadow_rank_socket.default_value = eu07_tools.mat.DEFAULT_VALUES["shadow_rank"]

        size_x_socket = ng.inputs.new("NodeSocketFloat", "Size X")
        size_x_socket.min_value = -1
        size_x_socket.default_value = eu07_tools.mat.DEFAULT_VALUES["size"][0]

        size_y_socket = ng.inputs.new("NodeSocketFloat", "Size Y")
        size_y_socket.min_value = -1
        size_y_socket.default_value = eu07_tools.mat.DEFAULT_VALUES["size"][1]

        opacity_socket = ng.inputs.new("NodeSocketFloat", "Opacity")
        opacity_socket.min_value = 0
        opacity_socket.max_value = 1
        opacity_socket.default_value = eu07_tools.mat.DEFAULT_VALUES["opacity"]

        selfillum_socket = ng.inputs.new("NodeSocketFloat", "SelfIllum")
        selfillum_socket.min_value = -1
        selfillum_socket.max_value = 2
        selfillum_socket.default_value = eu07_tools.mat.DEFAULT_VALUES["selfillum"]

    return ng


def register():
    bpy.utils.register_class(EU07_MATBlock)
    bpy.types.ShaderNodeGroup.eu07_matblock = bpy.props.PointerProperty(type=EU07_MATBlock)


def unregister():
    bpy.utils.unregister_class(EU07_MATBlock)
    del bpy.types.ShaderNodeGroup.eu07_matblock