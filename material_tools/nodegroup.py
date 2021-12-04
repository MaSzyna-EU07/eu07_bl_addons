import bpy

NODE_GROUP_NAME = "[EU07] Material Block"
MAX_TEXTURES_NUM = 8
VARIANT_NAMES = [
    "Spring",
    "Summer",
    "Autumn",
    "Winter",
    "Clear",
    "Cloudy",
    "Rain",
    "Snow"
]
DIFFUSE_TEXTURE_INDEX = 1
NORMAL_TEXTURE_INDEX = 2


def create_mat_nodegroup_template():
    ng = bpy.data.node_groups.get(NODE_GROUP_NAME)

    if ng is None:
        ng = bpy.data.node_groups.new(NODE_GROUP_NAME, 'ShaderNodeTree')

        ng_output = ng.nodes.new("NodeGroupOutput")
        ng.outputs.new("NodeSocketShader", "Output")

        bsdf = ng.nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs[5].default_value = 0 # specular
        bsdf.inputs[7].default_value = 1 # roughness
        ng.links.new(bsdf.outputs[0], ng_output.inputs[0])
        normal_map_node = ng.nodes.new("ShaderNodeNormalMap")
        ng.links.new(normal_map_node.outputs[0], bsdf.inputs[20])

        ng_input = ng.nodes.new("NodeGroupInput")

        ng.inputs.new("NodeSocketString", "Shader File")
        ng.inputs.new("NodeSocketString", "Shader Params")

        shadow_rank_socket = ng.inputs.new("NodeSocketInt", "Shadow Rank")
        shadow_rank_socket.min_value = 1
        shadow_rank_socket.max_value = 3

        size_x_socket = ng.inputs.new("NodeSocketFloat", "Size X")
        size_x_socket.min_value = -1
        size_x_socket.default_value = -1

        size_y_socket = ng.inputs.new("NodeSocketFloat", "Size Y")
        size_y_socket.min_value = -1
        size_y_socket.default_value = -1

        opacity_socket = ng.inputs.new("NodeSocketFloat", "Opacity")
        opacity_socket.min_value = 0
        opacity_socket.max_value = 1
        opacity_socket.default_value = 1

        selfillum_socket = ng.inputs.new("NodeSocketFloat", "SelfIllum")
        selfillum_socket.min_value = 0
        selfillum_socket.max_value = 2
        selfillum_socket.default_value = 0

        for texture_index in range(1, MAX_TEXTURES_NUM + 1):
            texture_socket = ng.inputs.new("NodeSocketColor", f"Texture{texture_index}")
            if texture_index == DIFFUSE_TEXTURE_INDEX:
                texture_socket.name = "Diffuse"
                ng.links.new(ng_input.outputs[7], bsdf.inputs[0])

                alpha_socket = ng.inputs.new("NodeSocketFloat", "Alpha")
                alpha_socket.min_value = 0
                alpha_socket.max_value = 1
                alpha_socket.default_value = 1

                ng.links.new(ng_input.outputs[8], bsdf.inputs[21])
            elif texture_index == NORMAL_TEXTURE_INDEX:
                texture_socket.name = "Normal Map"
                texture_socket.default_value = (0.5, 0.5, 1, 1)
                ng.links.new(ng_input.outputs[9], normal_map_node.inputs[1])

        for variant_name in VARIANT_NAMES:
            ng.inputs.new("NodeSocketShader", variant_name)

    return ng


def instantiate_mat_nodegroup(node_tree):
    ng = node_tree.nodes.new("ShaderNodeGroup")
    ng.node_tree = bpy.data.node_groups.get(
        NODE_GROUP_NAME,
        create_mat_nodegroup_template()
    )
    ng.label = NODE_GROUP_NAME

    return ng


def delete_mat_nodegroup_template():
    ng = bpy.data.node_groups[NODE_GROUP_NAME]
    if ng:
        bpy.data.node_groups.remove(ng)



