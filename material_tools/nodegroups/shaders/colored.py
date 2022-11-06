import eu07_tools


NODEGROUP_NAME = "[EU07] Colored"


def implement():
    ng = bpy.data.node_groups.get(NODEGROUP_NAME)
    if ng:
        bpy.data.node_groups.remove(ng)

    ng = bpy.data.node_groups.new(NODEGROUP_NAME, 'ShaderNodeTree')

    ng_output = ng.nodes.new("NodeGroupOutput")
    ng.outputs.new("NodeSocketShader", "Output")

    ng_input = ng.nodes.new("NodeGroupInput")

    input_color = ng.inputs.new("NodeSocketColor", "Color")
    input_diffuse = ng.inputs.new("NodeSocketFloat", "Diffuse")
    input_specular = ng.inputs.new("NodeSocketFloat", "Specular")
    input_reflection = ng.inputs.new("NodeSocketFloat", "Reflection")
    input_glossiness = ng.inputs.new("NodeSocketFloat", "Glossiness")

    bsdf = ng.nodes.new("ShaderNodeBsdfPrincipled")

    ng.links.new(
        bsdf.outputs[0],
        ng_output.inputs[0]
    )

    ng.links.new(
        ng_input.outputs[0],
        bsdf.inputs[0]
    )

    for variant_name in eu07_tools.mat.NESTED_MAPPING_KEYS:
        ng.inputs.new("NodeSocketShader", variant_name.capitalize())

    return ng