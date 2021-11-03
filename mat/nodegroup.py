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
        ng = bpy.data.node_groups.new(NODE_GROUP_NAME, 'ShaderNodeTree')

        ng_output = ng.nodes.new("NodeGroupOutput")
        ng.outputs.new("NodeSocketShader", "Output")

        bsdf = ng.nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs[5].default_value = 0 # specular
        bsdf.inputs[7].default_value = 1 # roughness
        ng.links.new(bsdf.outputs[0], ng_output.inputs[0])
        normal_map_node = ng.nodes.new("ShaderNodeNormalMap")
        ng.links.new(normal_map_node.outputs[0], bsdf.inputs[20])

        ng_input = ng.nodes.new("NodeGroupInput")

        ng.inputs.new("NodeSocketString", "Shader File")
        ng.inputs.new("NodeSocketString", "Shader Params")

        shadow_rank_socket = ng.inputs.new("NodeSocketInt", "Shadow Rank")
        shadow_rank_socket.min_value = 1
        shadow_rank_socket.max_value = 3

        size_x_socket = ng.inputs.new("NodeSocketFloat", "Size X")
        size_x_socket.min_value = -1
        size_x_socket.default_value = -1

        size_y_socket = ng.inputs.new("NodeSocketFloat", "Size Y")
        size_y_socket.min_value = -1
        size_y_socket.default_value = -1

        opacity_socket = ng.inputs.new("NodeSocketFloat", "Opacity")
        opacity_socket.min_value = 0
        opacity_socket.max_value = 1
        opacity_socket.default_value = 1

        selfillum_socket = ng.inputs.new("NodeSocketFloat", "SelfIllum")
        selfillum_socket.min_value = 0
        selfillum_socket.max_value = 2
        selfillum_socket.default_value = 0

        for texture_index in range(1, MAX_TEXTURES_NUM + 1):
            texture_socket = ng.inputs.new("NodeSocketColor", f"Texture{texture_index}")
            if texture_index == DIFFUSE_TEXTURE_INDEX:
                texture_socket.name = "Diffuse"
                ng.links.new(ng_input.outputs[7], bsdf.inputs[0])

                alpha_socket = ng.inputs.new("NodeSocketFloat", "Alpha")
                alpha_socket.min_value = 0
                alpha_socket.max_value = 1
                alpha_socket.default_value = 1

                ng.links.new(ng_input.outputs[8], bsdf.inputs[19])
            elif texture_index == NORMAL_TEXTURE_INDEX:
                texture_socket.name = "Normal Map"
                texture_socket.default_value = (0.5, 0.5, 1, 1)
                ng.links.new(ng_input.outputs[9], normal_map_node.inputs[1])

        for variant_name in VARIANT_NAMES:
            ng.inputs.new("NodeSocketShader", variant_name)

    return ng


def instantiate_mat_nodegroup(node_tree):
    ng = node_tree.nodes.new("ShaderNodeGroup")
    ng.node_tree = bpy.data.node_groups.get(
        NODE_GROUP_NAME,
        create_mat_nodegroup_template()
    )

    return ng


def delete_mat_nodegroup_template():
    ng = bpy.data.node_groups[NODE_GROUP_NAME]
    if ng:
        bpy.data.node_groups.remove(ng)



class NodeGroupWrapper:
    FIRST_TEXTURE_SOCKET_INDEX = 2

    def __init__(self, nodegroup, main_nodetree):
        self.nodegroup = nodegroup
        self.main_nodetree = main_nodetree

    def set_shader_name(self, shader_name):
        self.nodegroup.inputs[0].default_value = shader_name

    def get_shader_name(self):
        return self.nodegroup.inputs[0]

    def set_shader_params(self, shader_params):
        self.nodegroup.inputs[1].default_value = shader_params

    def get_shader_params(self):
        return self.nodegroup.inputs[1].default_valie

    def set_shadow_rank(self, shadow_rank):
        self.nodegroup.inputs[2].default_value = shadow_rank

    def get_shadow_rank(self):
        return self.nodegroup.inputs[2].default_value

    def set_size(self, size):
        self.nodegroup.inputs[3].default_value = size[0]
        self.nodegroup.inputs[4].default_value = size[1]

    def get_size(self):
        return (
            self.nodegroup.inputs[3].default_value,
            self.nodegroup.inputs[4].default_value
        )

    def set_opacity(self, opacity):
        self.nodegroup.inputs[5].default_value = opacity

    def get_opacity(self):
        return self.nodegroup.inputs[5].default_value

    def set_selfillum(self, selfillum):
        self.nodegroup.inputs[6].default_value = selfillum

    def get_selfillum(self):
        return self.nodegroup.inputs[6]

    def set_texture_image(self, texture_image, index, alias=""):
        texture_input = self._get_texture_input(index)
        if texture_input.links:
            texture_link = texture_input.links[0]
            texture_node = texture_link.from_node
            texture_node.image = texture_image

        else:
            texture_node = self.main_nodetree.nodes.new("ShaderNodeTexImage")
            texture_node.image = texture_image
            texture_node.label = alias if alias else texture_image.name

            texture_input = self._get_texture_input(index)
            self.main_nodetree.links.new(texture_node.outputs[0], texture_input)

            if index == DIFFUSE_TEXTURE_INDEX:
                alpha_input_index = self.nodegroup.inputs.find(texture_input.name) + 1
                self.main_nodetree.links.new(texture_node.outputs[1], self.nodegroup.inputs[alpha_input_index])

    def get_texture_image(self, index):
        texture_input = self._get_texture_input(index)
        if texture_input.links:
            texture_link = texture_input.links[0]
            texture_node = texture_link.from_node

            if texture_node.image:
                return texture_node.image

        return None

    def _get_texture_input(self, index):
        for input_ in self.nodegroup.inputs:
            if index == 1 and input_.name == "Diffuse":
                return input_
            elif index == 2 and input_.name == "Normal Map":
                return  input_
            elif "Texture" in input_.name:
                if int(input_.name[-1]) == index:
                    return input_


    def set_nested(self, key, nested_wrapper):
        input_ = self._get_nested_input(key)
        if input_.name.lower() == key:
            self.main_nodetree.links.new(nested_wrapper.nodegroup.outputs[0], input_)

    def get_nested(self, key):
        input_ = self._get_nested_input(key)
        if input_.links:
            return NodeGroupWrapper(input_.links[0].from_node, self.main_nodetree)

    def _get_nested_input(self, key):
        for input_ in self.nodegroup.inputs:
            if input_.name.lower() == key:
                return input_
