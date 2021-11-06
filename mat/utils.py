import bpy

from common.utils import get_qualified_material_name


def create_material_from_image_path(filepath):
    name = get_qualified_material_name(filepath)
    material = bpy.data.materials.new(name)

    material.use_nodes = True

    for node in material.node_tree.nodes:
        material.node_tree.nodes.remove(node)

    material_output = material.node_tree.nodes.new("ShaderNodeOutputMaterial")
    material_output.location = (200, 0)

    bsdf = material.node_tree.nodes.new("ShaderNodeBsdfDiffuse")
    bsdf.location = (0, 0)

    image_node = material.node_tree.nodes.new("ShaderNodeTexImage")
    image = bpy.data.images.load(filepath, check_existing=True)
    image_node.image = image
    image_node.location = (-300, 0)

    material.node_tree.links.new(image_node.outputs[0], bsdf.inputs[0])
    material.node_tree.links.new(bsdf.outputs[0], material_output.inputs[0])

    return material