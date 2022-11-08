import bpy

RANDOM_TEXTURESET_NAME = "[EU07] Random Texture Set"
MAX_TEXTURESET_SIZE = 4


def generate():
    ng = bpy.data.node_groups.get(RANDOM_TEXTURESET_NAME)

    if ng is None:
        ng = bpy.data.node_groups.new(RANDOM_TEXTURESET_NAME, 'ShaderNodeTree')

        ng_output = ng.nodes.new("NodeGroupOutput")
        ng_input = ng.nodes.new("NodeGroupInput")

        ng.outputs.new("NodeSocketColor", "Output Texture")
        for i in range(MAX_TEXTURESET_SIZE):
            ng.inputs.new("NodeSocketColor", f"Texture{i+1}")

        ng.links.new(
            ng_input.outputs[0],
            ng_output.inputs[0]
        )

    return ng