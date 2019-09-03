from pathlib import Path

import bpy
import eu07_tools


def get_root(abspath):
    try:
        root = eu07_tools.utils.find_asset_root(abspath)
    except ValueError:
        root = bpy.context.preferences.addons['eu07_bl_addons'].preferences.root
        if not root:
            raise ValueError(f"Can't find root path for {abspath}")

    return root

def create_material_from_path(abspath, duplicates_allowed):
    name = Path(abspath).with_suffix("").name

    if not duplicates_allowed and name in bpy.data.materials:
        return bpy.data.materials[name]

    # TODO: Load materials from .mat
    try:
        img = bpy.data.images.load(abspath, check_existing=True)
    except:
        return None

    material = bpy.data.materials.new(name)
    material.use_nodes = True

    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs[5].default_value = 0

    texture_node = material.node_tree.nodes.new("ShaderNodeTexImage")
    texture_node.name = "texture_diffuse"
    texture_node.label = "texture_diffuse"
    texture_node.image = img

    material.node_tree.links.new(
        texture_node.outputs[0],
        bsdf.inputs[0]
    )

    if abspath.endswith(".dds"):
        texture_node.texture_mapping.scale[1] = -1

    return material
