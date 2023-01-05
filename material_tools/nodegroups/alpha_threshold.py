import bpy

from material_tools.utils import ALPHA_THRESHOLD_NAME

def generate():
    ng = bpy.data.node_groups.get(ALPHA_THRESHOLD_NAME)

    if ng is None:
        ng = bpy.data.node_groups.new(ALPHA_THRESHOLD_NAME, 'ShaderNodeTree')

        ng_output = ng.nodes.new("NodeGroupOutput")
        ng_input = ng.nodes.new("NodeGroupInput")

        input_alpha = ng.inputs.new("NodeSocketFloat", "Alpha")
        input_alpha.default_value = 1
        input_alpha.hide_value = True

        input_threshold = ng.inputs.new("NodeSocketFloat", "Threshold")
        input_threshold.default_value = 0.5

        ng.outputs.new("NodeSocketFloat", "Alpha")



    return ng



