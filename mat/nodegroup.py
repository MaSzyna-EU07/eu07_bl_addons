import bpy

NODE_GROUP_NAME = "[EU07] Material"
MAX_TEXTURES_NUM = 8
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
DIFFUSE_TEXTURE_INDEX = 1
NORMAL_TEXTURE_INDEX = 2


def create_mat_nodegroup_template():
    ng = bpy.data.node_groups.get(NODE_GROUP_NAME)

    if ng is None:
        ng = bpy.data.node_groups.new(NODE_GROUP_NAME, 'DUMMY')

        ng_output = ng.nodes.new("ShaderNodeGroupOutput")
        ng_output.inputs.new("NodeSocketShader", "Output")

        bsdf = ng.nodes.new("ShaderNodeBsdfPrincipled")
        ng.links(bsdf.outputs[0], ng_output.inputs.get("Output"))
        normal_map_node = ng.nodes.new("ShaderNodeNormalMap")
        ng.links.new(normal_map_node.outputs[0], bsdf.inputs[19])

        ng_input = ng.nodes.new("ShaderNodeGroupInput")

        ng_input.inputs.new("NodeSocketString", "Shader File")
        ng_input.inputs.new("NodeSocketString", "Shader Params")

        for texture_index in range(MAX_TEXTURES_NUM):
            texture_socket = ng_input.inputs.new("NodeSocketColor", f"Texture{texture_index}")
            if texture_index == DIFFUSE_TEXTURE_INDEX:
                ng.links.new(texture_socket, bsdf.inputs.get("Base Color"))
            elif texture_index == NORMAL_TEXTURE_INDEX:
                ng.links.new(texture_socket, normal_map_node.inputs[1])

        shadow_rank_socket = ng_input.inputs.new("NodeSocketInt", "Shadow Rank")
        shadow_rank_socket.min_value = 1
        shadow_rank_socket.max_value = 3

        size_x_socket = ng_input.inputs.new("NodeSocketFloat", "Size X")
        size_x_socket.min_value = -1
        size_x_socket.default_value = -1

        size_y_socket = ng_input.inputs.new("NodeSocketFloat", "Size Y")
        size_y_socket.min_value = -1
        size_y_socket.default_value = -1

        opacity_socket = ng_input.inputs.new("NodeSocketFloat", "Opacity")
        opacity_socket.min_value = 0
        opacity_socket.max_value = 1
        opacity_socket.default_value = 1

        selfillum_socket = ng_input.inputs.new("NodeSocketFloat", "SelfIllum")
        selfillum_socket.min_value = 0
        selfillum_socket.max_value = 2
        selfillum_socket.default_value = 0

        for variant_name in VARIANT_NAMES:
            ng_input.inputs.new("NodeSocketShader", variant_name)

    return ng


def instantiate_mat_nodegroup(node_tree):
    ng = node_tree.nodes.new("ShaderNodeGroup")
    ng.node_tree = bpy.data.node_groups.get(
        NODE_GROUP_NAME,
        create_mat_nodegroup_template()
    )


def delete_mat_nodegroup_template():
    ng = bpy.data.node_groups[NODE_GROUP_NAME]
    if ng:
        bpy.data.node_groups.remove(ng)



class NodeGroupWrapper:
    FIRST_TEXTURE_SOCKET_INDEX = 2

    def __init__(self, nodegroup):
        self.nodegroup = nodegroup
        self._nodes = nodegroup.nodes
        self._links = nodegroup.links
        self._inputs = self.nodegroup.inputs
        self._outputs = self.nodegroup.outputs

    def set_shader_name(self, shader_name):
        self._inputs[0].default_value = shader_name

    def get_shader_name(self):
        return self._inputs[0]

    def set_shader_params(self, shader_params):
        self._inputs[1].default_value = shader_params

    def set_texture_image(self, texture_image, index, alias=""):
        texture_input = self._get_texture_input(index)
        if texture_input.links:
            texture_link = texture_input.links[0]
            texture_node = texture_link.from_node
            texture_node.image = texture_image

        else:
            texture_node = self._nodes.new("ShaderNodeTexImage")
            texture_node.image = texture_image
            texture_node.label = alias if alias else texture_image.name

            self._links.new(texture_node.outputs[0], self._get_texture_input(index))

    def get_texture_image(self, index):
        texture_input = self._get_texture_input(index)
        if texture_input.links:
            texture_link = texture_input.links[0]
            texture_node = texture_link.from_node

            if texture_node.image:
                return texture_node.image

        return None

    def _get_texture_input(self, index):
        # -1 because textures are indexed from 1
        return self._inputs[self.FIRST_TEXTURE_SOCKET_INDEX + index - 1]

    def get_shader_params(self):
        return self._inputs[1].default_valie

    def set_shadow_rank(self, shadow_rank):
        self._inputs[10].default_value = shadow_rank

    def get_shadow_rank(self):
        return self._inputs[10].default_value

    def set_size(self, size):
        self._inputs[11].default_value = size[0]
        self._inputs[12].default_value = size[1]

    def get_size(self):
        return (
            self._inputs[11].default_value,
            self._inputs[12].default_value
        )

    def set_opacity(self, opacity):
        self._inputs[13].default_value = opacity

    def get_opacity(self):
        return self._inputs[13].default_value

    def set_selfillum(self, selfillum):
        self._inputs[14].default_value = selfillum

    def get_selfillum(self):
        return self._inputs[14]

    def set_nested(self, key, nested_wrapper):
        input_ = self._get_nested_input(key)
        if input_.name.lower() == key:
            self._links.new(nested_wrapper.nodegroup.outputs[0], input_)

    def get_nested(self, key):
        input_ = self._get_nested_input(key)
        if input_.links:
            return NodeGroupWrapper(input_.links[0].from_node)

    def _get_nested_input(self, key):
        for input_ in self._inputs:
            if input_.name.lower() == key:
                return input_
