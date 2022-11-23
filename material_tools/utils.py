import pathlib
import bpy

import common
import eu07_tools

def create_material(name):
    bl_material = bpy.data.materials.new(name)
    return bl_material


def get_active_material(context):
    active_object = context.view_layer.objects.active
    if active_object:
        active_material = active_object.active_material
        return active_material


def get_active_material_node(material):
    if material:
        return material.node_tree.nodes.active


def get_qualified_material_name(abspath, opacity=1):
    root = common.utils.get_environment_path(abspath)

    try:
        name = str(pathlib.Path(abspath).relative_to(root).with_suffix(""))

        if opacity < 1:
            name += "_Transparent"

        return name
    except ValueError:
        return ""


def get_shortpath_from_material(material):
    raise DeprecationWarning("get_shortpath_from_material is legacy and should be removed. Returning none...")
    return "none"


def get_filename_from_material(material):
    raise DeprecationWarning("get_filename_from_material is legacy and should be removed. Returning none...")
    return "none"


SHADER_NAME_PREFIX = "[EU07] Shader: "
RANDOM_TEXTURESET_NAME = "[EU07] Random Texture Set"

BSDF_COLOR_INPUT = 0
BSDF_SPECULAR_INPUT = 7
BSDF_ROUGHNESS_INPUT = 9
BSDF_ALPHA_INPUT = 21
BSDF_METALLIC_INPUT = 6
BSDF_NORMAL_INPUT = 22


def is_eu07_shader_node(node):
    return (
        node.bl_idname == "ShaderNodeGroup" and
        node.node_tree is not None
        and node.node_tree.name.startswith(SHADER_NAME_PREFIX)
    )


def is_random_textureset_node(node):
    return (
        node.bl_idname == "ShaderNodeGroup" and
        node.node_tree is not None and
        node.node_tree.name == RANDOM_TEXTURESET_NAME
    )


