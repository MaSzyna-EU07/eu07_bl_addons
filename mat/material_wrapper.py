from .nodegroup import NODE_GROUP_NAME

class MaterialWrapper:
    def __init__(self, material):
        self._material = material

    def _get_main_block(self):
        for node in self._material.nodes:
            if node.label == NODE_GROUP_NAME and node.outputs:
                link = node.links[0]


    def _get_material_output(self):
        for node in self._material.nodes:
            if node.bl_idname == 'ShaderNodeOutputMaterial':
                return node
            else:
                return self._material.nodes.new('ShaderNodeOutputMaterial')

class BlockWrapper:
    def __init__(self, node_group, material):
        self._node_group = node_group
        self._material = material