import bpy

from material_tools.utils import WRAP_TRAITS_NAME

def generate():
    ng = bpy.data.node_groups.get(WRAP_TRAITS_NAME)

    if ng is None:
        ng = bpy.data.node_groups.new(WRAP_TRAITS_NAME, 'ShaderNodeTree')

        ng_output = ng.nodes.new("NodeGroupOutput")
        ng_input = ng.nodes.new("NodeGroupInput")

        ng.inputs.new("NodeSocketInt", "Disable Horizontal (S)")
        ng.inputs.new("NodeSocketInt", "Disable Vertical (T)")

        ng.outputs.new("NodeSocketVector", "Vector")

        sep_xyz = ng.nodes.new("ShaderNodeSeparateXYZ")
        comb_xyz = ng.nodes.new("ShaderNodeCombineXYZ")

        ng.links.new(
            comb_xyz.outputs[0],
            ng_output.inputs[0]
        )

        ng.links.new(
            ng_input.outputs[0],
            sep_xyz.inputs[0]
        )

        x_last_socket = _generate_wrap_chain(ng, sep_xyz.outputs[0], ng_input.outputs[1])
        ng.links.new(
            x_last_socket,
            comb_xyz.inputs[0]
        )

        y_last_socket = _generate_wrap_chain(ng, sep_xyz.outputs[1], ng_input.outputs[2])
        ng.links.new(
            y_last_socket,
            comb_xyz.inputs[1]
        )

    return ng

def _generate_wrap_chain(ng, coord_output, param_output):
    add = ng.nodes.new("ShaderNodeMath")
    add.operation = 'ADD'

    mul1 = ng.nodes.new("ShaderNodeMath")
    mul1.operation = 'MULTIPLY'

    mul2 = ng.nodes.new("ShaderNodeMath")
    mul2.operation = 'MULTIPLY'

    clamp = ng.nodes.new("ShaderNodeClamp")
    clamp.inputs[1].default_value = 0
    clamp.inputs[2].default_value = 0.99999

    sub = ng.nodes.new("ShaderNodeMath")
    sub.operation = 'MULTIPLY'

    ng.links.new(
        mul1.outputs[0],
        add.inputs[0],
    )
    ng.links.new(
        mul2.outputs[0],
        add.inputs[1],
    )
    ng.links.new(
        sub.outputs[0],
        mul1.inputs[0]
    )
    ng.links.new(
        coord_output,
        mul1.inputs[0]
    )
    ng.links.new(
        coord_output,
        clamp.inputs[0]
    )
    ng.links.new(
        clamp.outputs[0],
        mul2.inputs[0]
    )
    ng.links.new(
        param_output,
        mul2.inputs[0]
    )
    ng.links.new(
        param_output,
        sub.inputs[1]
    )

    last_socket = add.outputs[0]
    return last_socket



