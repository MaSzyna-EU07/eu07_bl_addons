import pathlib

import eu07_tools
import common
from .nodegroup import NODE_GROUP_NAME


def get_qualified_material_name(abspath):
    root = common.utils.get_root(abspath)
    return str(pathlib.Path(abspath).relative_to(root).with_suffix(""))


def get_shortpath_from_material(material):
    if material:
        if is_mat_material(material):
            path = pathlib.Path(material.name)
            if "textures" in path.parts:
                return str(path.relative_to("textures").with_suffix(""))

        elif is_texture_material(material):
            node = get_node_tree_output_connection(material.node_tree)
            if node:
                color_input_socket = node.inputs[0]

                if color_input_socket.links:
                    image_node = color_input_socket.links[0].from_node
                    return eu07_tools.utils.shorten_asset_path(image_node.image.filepath)

    return "none"


def is_texture_material(material):
    if material.use_nodes:
        node = get_node_tree_output_connection(material.node_tree)
        if node:
            return _is_bsdf_node(node)


def is_mat_material(material):
    if material.use_nodes:
        node = get_node_tree_output_connection(material.node_tree)
        if node:
            return node.label == NODE_GROUP_NAME


def get_node_tree_output_connection(node_tree):
    output_node = node_tree.get_output_node('ALL')
    if output_node:
        links = output_node.inputs[0].links
        if links:
            return links[0].from_node

    return None


def ensure_correct_image_node_settings(image_node):
    if image_node.image.filepath.endswith(".dds"):
        image_node.texture_mapping.scale = (1, -1, 1)
    else:
        image_node.texture_mapping.scale = (1, 1, 1)


def ensure_correct_principled_bsdf_settings(bsdf):
    bsdf.inputs[5].default_value = 0 # Specular
    bsdf.inputs[7].default_value = 1 # Roughness


def _is_bsdf_node(node):
    return 'Bsdf' in node.bl_idname