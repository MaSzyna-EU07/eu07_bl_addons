import eu07_tools
from material_tools.nodegroups.utils import BSDF_COLOR_INPUT, BSDF_ALPHA_INPUT, BSDF_METALLIC_INPUT, BSDF_ROUGHNESS_INPUT

NODEGROUP_NAME = "[EU07] phys_normalmap"


def implement():
    ng = bpy.data.node_groups.get(NODEGROUP_NAME)
    if ng:
        bpy.data.node_groups.remove(ng)

    ng = bpy.data.node_groups.new(NODEGROUP_NAME, 'ShaderNodeTree')

    # all nodes creation here
    ng_input = ng.nodes.new("NodeGroupInput")
    ng_output = ng.nodes.new("NodeGroupOutput")
    bsdf = ng.nodes.new("ShaderNodeBsdfPrincipled")
    mix_rgb = ng.nodes.new("ShaderNodeMixRGB")
    mix_rgb.blend_type = 'MULTIPLY'
    sep_rgb = ng.nodes.new("ShaderNodeSeparateColor")
    invert = ng.nodes.new("ShaderNodeInvert")


    # node group inputs and outputs...
    input_albedo = ng.inputs.new("NodeSocketColor", "Albedo Map")
    input_alpha = ng.inputs.new("NodeSocketFloat", "Alpha")
    input_params = ng_input.new("NodeSocketColor", "Params Map")
    input_nrm = ng_input.new("NodeSocketColor", "Normal Map")

    shader_output = ng.outputs.new("NodeSocketShader", "Output")

    # link albedo to mix color
    ng.links.new(
        ng_input.outputs[0],
        mix_rgb.inputs[0]
    )
    # link mix color to bsdf input
    ng.links.new(
        mix_rgb.outputs[0],
        bsdf.inputs[BSDF_COLOR_INPUT]
    )
    # link alpha input to bsdf's alpha
    ng.links.new(
        ng_input.outputs[1],
        bsdf.inputs[BSDF_ALPHA_INPUT]
    )
    # link params map to color separator
    ng.links.new(
        ng_input.outputs[2],
        sep_rgb.inputs[0]
    )
    # link separated R to bsdf's metallic
    ng.links.new(
        sep_rgb.outputs[0],
        bsdf.inputs[BSDF_METALLIC_INPUT]
    )
    # link separated G to invert
    ng.links.new(
        sep_rgb.outputs[1],
        invert.inputs[0]
    )
    # link inverted G to bsdf's roughness
    ng.links.new(
        invert.outputs[0],
        bsdf.inputs[BSDF_ROUGHNESS_INPUT]
    )
    # link separated B to mix color (this is AO)
    ng.links.new(
        sep_rgb.outputs[2],
        mix_rgb.inputs[1]
    )

    for variant_name in eu07_tools.mat.NESTED_MAPPING_KEYS:
        ng.inputs.new("NodeSocketShader", variant_name.capitalize())

    return ng