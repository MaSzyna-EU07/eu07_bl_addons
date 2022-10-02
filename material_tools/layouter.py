import mathutils

NODE_DIMENSIONS = {
    "ShaderNodeBsdfPrincipled": (240.0, 660.0),
    "ShaderNodeGroup": (140.0, 589.0),
    "ShaderNodeTexImage": (240.0, 277.0),
}

class NodeLayouter:
    def __init__(self, material):
        self.material = material

    def layout_nodes(self):
        first = self._find_first_node()
        self._arrange_children(first)
        if self.material.eu07_material.is_mat:
            mat_root_node = self.material.eu07_material.mat_root.bl_node
            mat_root_node.location = first.location - mathutils.Vector((500, 660))
            self._arrange_children(mat_root_node)

    def _find_first_node(self):
        for node in self.material.node_tree.nodes:
            if node.bl_idname == "ShaderNodeOutputMaterial":
                return node

    def _arrange_children(self, node):
        loc_y = node.location.y

        for input_ in node.inputs:
            if input_.links:
                subnode = input_.links[0].from_node
                if subnode:
                    subnode_dims = NODE_DIMENSIONS.get(subnode.bl_idname, (240, 500))
                    subnode.location.x = node.location.x - 500
                    subnode.location.y = loc_y
                    loc_y = loc_y - subnode_dims[1]

                    self._arrange_children(subnode)
