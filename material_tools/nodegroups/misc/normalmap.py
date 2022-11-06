import eu07_tools


NODEGROUP_NAME = "[EU07] Normal Map"


def create(target_node_tree):
    node = target_node_tree.nodes.new("ShaderNodeGroup")
    node.node_tree = bpy.data.node_groups[NODEGROUP_NAME]


def get_instance():
    ng = bpy.data.node_groups.get(NODEGROUP_NAME)
    if ng is None:
        ng = implement()

    return ng


def implement():
    ng = bpy.data.node_groups.get(NODEGROUP_NAME)
    if ng:
        bpy.data.node_groups.remove(ng)

    ng = bpy.data.node_groups.new(NODEGROUP_NAME, 'ShaderNodeTree')

    ng_output = ng.nodes.new("NodeGroupOutput")
    ng.outputs.new("NodeSocketShader", "Output")

    ng_input = ng.nodes.new("NodeGroupInput")

    input_color = ng.inputs.new("NodeSocketColor", "Color")

    sep = ng.nodes.new("ShaderNodeSeparateColor")
    comb = ng.nodes.new("ShaderNodeCombineColor")
    nrm = ng.nodes.new("ShaderNodeNormalMap")

    # input color to Separate
    ng.links.new(
        ng_input.outputs[0],
        sep.inputs[0]
    )

    # R to R
    ng.links.new(
        sep.outputs[0],
        comb.inputs[0]
    )

    # G to G
    ng.links.new(
        sep.outputs[1],
        comb.inputs[1]
    )

    # B = 1
    comb.inputs[2].default_value = 1

    # Combined to Normal Map
    ng.links.new(
        comb.outputs[0],
        nrm.inputs[0]
    )

    # Normal Map to output
    ng.links.new(
        nrm.outputs[0],
        ng_output.inputs[0]
    )

    return ng