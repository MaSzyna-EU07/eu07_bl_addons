from .nodegroup import NODE_GROUP_NAME, DIFFUSE_TEXTURE_INDEX, NORMAL_TEXTURE_INDEX, MAX_TEXTURES_NUM, instantiate_mat_nodegroup


class MaterialWrapper:
    def __init__(self, material):
        self._material = material

    def do_basic_setup(self):
        self._material.use_backface_culling = True
        self._material.blend_method = 'CLIP'
        self._material.use_nodes = True

        for node in self._material.node_tree.nodes:
            self._material.node_tree.nodes.remove(node)

        self._material.node_tree.nodes.new('ShaderNodeOutputMaterial')

    def get_main_block(self):
        for node in self._material.node_tree.nodes:
            if node.label == NODE_GROUP_NAME:
                output = node.outputs[0]

                is_nested = any([link.to_node.label == NODE_GROUP_NAME for link in output.links])
                if not is_nested:
                    return BlockWrapper(node, self, self._material.node_tree)

        return None

    def create_block(self):
        return BlockWrapper(instantiate_mat_nodegroup(self._material.node_tree), self, self._material.node_tree)


class BlockWrapper:

    def __init__(self, node_group, material_wrapper, material_node_tree):
        self._node_group = node_group
        self._material_wrapper = material_wrapper
        self._material_node_tree = material_node_tree

    @property
    def node_group_output_socket(self):
        return self._node_group.outputs[0]

    def make_active(self):
        for node in self._material_node_tree.nodes:
            if node.bl_idname == 'ShaderNodeOutputMaterial':
                material_output = node

        if material_output:
            self._material_node_tree.links.new(
                self._node_group.outputs[0],
                material_output.inputs[0]
            )

    def set_sub_block(self, identifier, sub_block):
        input_socket = self._get_sub_block_input_socket(identifier)
        self._material_node_tree.links.new(
            sub_block.node_group_output_socket,
            input_socket
        )

    def get_sub_block(self, identifier):
        input_socket = self._get_sub_block_input_socket(identifier)
        if input_socket and input_socket.links and input_socket.links[0].from_node:
            return BlockWrapper(input_socket.links[0].from_node, self._material_wrapper, self._material_node_tree)

        return None

    def _get_sub_block_input_socket(self, identifier):
        FIRST_SUBBLOCK_SOCKET_INDEX = 16
        for input_socket in self._node_group.inputs[FIRST_SUBBLOCK_SOCKET_INDEX:]:
            if input_socket and input_socket.name.lower() == identifier.lower():
                return input_socket

    def get_parent_block(self):
        if self._node_group.outputs[0].links:
            to_node = self._node_group.outputs[0].links[0].to_node
            if to_node.label == NODE_GROUP_NAME:
                return BlockWrapper(to_node)

    def set_shader_name(self, shader_name):
        self._node_group.inputs[0].default_value = shader_name

    def get_shader_name(self):
        return self._node_group.inputs[0]

    def set_shader_params(self, shader_params):
        self._node_group.inputs[1].default_value = shader_params

    def get_shader_params(self):
        return self._node_group.inputs[1].default_value

    def set_shadow_rank(self, shadow_rank):
        self._node_group.inputs[2].default_value = shadow_rank

    def get_shadow_rank(self):
        return self._node_group.inputs[2].default_value

    def set_size(self, size):
        self._node_group.inputs[3].default_value = size[0]
        self._node_group.inputs[4].default_value = size[1]

    def get_size(self):
        return (
            self._node_group.inputs[3].default_value,
            self._node_group.inputs[4].default_value
        )

    def set_opacity(self, opacity):
        self._node_group.inputs[5].default_value = opacity

    def get_opacity(self):
        return self._node_group.inputs[5].default_value

    def set_selfillum(self, selfillum):
        self._node_group.inputs[6].default_value = selfillum

    def get_selfillum(self):
        return self._node_group.inputs[6]

    def set_texture_image(self, texture_image, index, alias=""):
        texture_input = self._get_texture_input(index)

        if texture_input.links:
            texture_link = texture_input.links[0]
            texture_node = texture_link.from_node
            texture_node.image = texture_image

        else:
            texture_node = self._material_node_tree.nodes.new("ShaderNodeTexImage")
            texture_node.image = texture_image
            texture_node.label = alias if alias else texture_image.name

            texture_input = self._get_texture_input(index)
            self._material_node_tree.links.new(
                texture_node.outputs[0],
                texture_input
            )

            if index == DIFFUSE_TEXTURE_INDEX:
                alpha_input_index = self._node_group.inputs.find(texture_input.name) + 1
                self._material_node_tree.links.new(
                    texture_node.outputs[1],
                    self._node_group.inputs[alpha_input_index]
                )
            elif index == NORMAL_TEXTURE_INDEX:
                texture_image.colorspace_settings.name = "Non-Color"

        if texture_image.filepath.endswith(".dds"):
            texture_node.texture_mapping.scale = (1, -1, 1)
        else:
            texture_node.texture_mapping.scale = (1, 1, 1)

    def get_texture_image(self, index):
        texture_input = self._get_texture_input(index)
        if texture_input.links:
            texture_link = texture_input.links[0]
            texture_node = texture_link.from_node

            if texture_node.image:
                return texture_node.image

        return None

    def _get_texture_input(self, index):
        FIRST_TEXTURE_SOCKET_INDEX = 7
        inputs = self._node_group.inputs[
                 FIRST_TEXTURE_SOCKET_INDEX:
                 FIRST_TEXTURE_SOCKET_INDEX + MAX_TEXTURES_NUM
        ]

        for input_ in inputs:
            if index == 1 and input_.name == "Diffuse":
                return input_
            elif index == 2 and input_.name == "Normal Map":
                return input_
            elif "Texture" in input_.name:
                if int(input_.name[-1]) == index:
                    return input_

