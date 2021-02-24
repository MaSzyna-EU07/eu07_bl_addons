from pathlib import Path

import bpy
import eu07_tools
from eu07_tools.utils import AssetSearcher


def get_root(abspath=""):
    try:
        root = eu07_tools.utils.find_asset_root(abspath)
    except ValueError:
        root = bpy.context.preferences.addons['eu07_bl_addons'].preferences.root
        if not root:
            raise ValueError(f"Can't find root path for {abspath}")

    return root


def create_material_from_relpath(relpath, duplicated_allowed=False):
    asset_searcher = AssetSearcher(get_root())
    asset_searcher.textures.remove_extension(".mat")

    abspath = asset_searcher.textures.find(relpath)
    return create_material_from_abspath(abspath, duplicated_allowed)


def create_material_from_abspath(abspath, duplicates_allowed=False):
    if abspath == "":
        return None

    name = Path(abspath).relative_to(get_root()).with_suffix("").name

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

    alpha_input = next(inp for inp in bsdf.inputs if inp.name == "Alpha")

    material.node_tree.links.new(
        texture_node.outputs[1],
        alpha_input
    )

    material.blend_method = 'CLIP'
    material.use_backface_culling = True

    if abspath.endswith(".dds"):
        texture_node.texture_mapping.scale[1] = -1

    return material


def get_path_from_material(material):
    if material:
        if material.use_nodes:
            # Get the nodes in the node tree
            nodes = material.node_tree.nodes
            # Get a principled node
            principled = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
            # Get the slot for 'base color'
            base_color = principled.inputs['Base Color']  # Or principled.inputs[0]
            link = base_color.links[0]
            link_node = link.from_node
            return eu07_tools.utils.shorten_asset_path(link_node.image.filepath)

    return "none"
