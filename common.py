import bpy

def create_material_from_path(name, abspath):
    try:
        img = bpy.data.images.load(abspath, check_existing=True)
    except:
        return None

    material = bpy.data.materials.new(name)
    material.use_nodes = True

    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs[5].default_value = 0

    texture_node = material.node_tree.nodes.new("ShaderNodeTexImage")
    texture_node.image = img

    material.node_tree.links.new(
        texture_node.outputs[0],
        bsdf.inputs[0]
    )

    if abspath.endswith(".dds"):
        texture_node.texture_mapping.scale[1] = -1

    return material