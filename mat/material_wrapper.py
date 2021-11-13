from .nodegroup import NODE_GROUP_NAME, DIFFUSE_TEXTURE_INDEX, NORMAL_TEXTURE_INDEX


class NodeTreeManager:
    def __init__(self, material):
        self._material = material
        self._nodes = material.node_tree.nodes
        self._links = material.node_tree.links

    def get_main_block_node(self):
        for node in self._nodes:

            if node.label == NODE_GROUP_NAME:
                output = node.outputs[0]

                if output.links:
                    link = output.links[0]
                    connected_node = link.to_node

                    if connected_node and connected_node.label != NODE_GROUP_NAME:
                        return node

    def get_subblock_node(self, block_node, identifier):
        for input_ in block_node.inputs:
            if input_.name.lower() == identifier:
                if input_.links:
                    return input_.links[0].from_node

    def set_subblock_node(self, block_node, identifier):
        pass

    def set_image(self, block_node, image, index, alias=""):
        texture_input = self._get_texture_input(block_node, index)

        if texture_input.links:
            texture_link = texture_input.links[0]
            texture_node = texture_link.from_node
            texture_node.image = image

        else:
            texture_node = self._nodes.new("ShaderNodeTexImage")
            texture_node.image = image
            texture_node.label = alias if alias else image.name

            self._owner_node_tree.links.new(
                texture_node.outputs[0],
                self._get_texture_input(index)
            )

            if index == DIFFUSE_TEXTURE_INDEX:
                alpha_input_index = self.node_group.inputs.find(texture_input.name) + 1
                self._owner_node_tree.links.new(
                    texture_node.outputs[1],
                    self.node_group.inputs[alpha_input_index]
                )
            elif index == NORMAL_TEXTURE_INDEX:
                image.colorspace_settings.name = "Non-Color"

        if image.filepath.endswith(".dds"):
            texture_node.texture_mapping.scale = (1, -1, 1)
        else:
            texture_node.texture_mapping.scale = (1, 1, 1)

    def get_texture_image(self, block_node, index):
        texture_input = self._get_texture_input(block_node, index)
        if texture_input.links:
            texture_link = texture_input.links[0]
            texture_node = texture_link.from_node

            if texture_node and texture_node.image:
                return texture_node.image

        return None

    def _get_texture_input(self, block_node, index):
        for input_ in block_node.inputs:
            if index == 1 and input_.name == "Diffuse":
                return input_
            elif index == 2 and input_.name == "Normal Map":
                return  input_
            elif "Texture" in input_.name:
                if int(input_.name[-1]) == index:
                    return input_




class MATMaterialWrapper:
    def __init__(self, material):
        self._material = material
        self._nodes = material.node_tree.nodes
        self._links = material.node_tree.links

    def get_main_block(self):
        for node in self._nodes:

            if node.label == NODE_GROUP_NAME:
                output = node.outputs[0]

                if output.links:
                    link = output.links[0]
                    connected_node = link.to_node

                    if connected_node and connected_node.label != NODE_GROUP_NAME:
                        return MATBlockWrapper(node, self._material.node_tree)

        return None


class MATBlockWrapper:
    def __init__(self, node_group, owner_node_tree):
        self._owner_node_tree = owner_node_tree
        self.node_group = node_group

    def set_shader_name(self, shader_name):
        self.node_group.inputs[0].default_value = shader_name

    def get_shader_name(self):
        return self.node_group.inputs[0]

    def set_shader_params(self, shader_params):
        self.node_group.inputs[1].default_value = shader_params

    def get_shader_params(self):
        return self.node_group.inputs[1].default_value

    def set_shadow_rank(self, shadow_rank):
        self.node_group.inputs[2].default_value = shadow_rank

    def get_shadow_rank(self):
        return self.node_group.inputs[2].default_value

    def set_size(self, size):
        self.node_group.inputs[3].default_value = size[0]
        self.node_group.inputs[4].default_value = size[1]

    def get_size(self):
        return (
            self.node_group.inputs[3].default_value,
            self.node_group.inputs[4].default_value
        )

    def set_opacity(self, opacity):
        self.node_group.inputs[5].default_value = opacity

    def get_opacity(self):
        return self.node_group.inputs[5].default_value

    def set_selfillum(self, selfillum):
        self.node_group.inputs[6].default_value = selfillum

    def get_selfillum(self):
        return self.node_group.inputs[6]

    def get_output(self):
        return self.node_group.outputs[0]

