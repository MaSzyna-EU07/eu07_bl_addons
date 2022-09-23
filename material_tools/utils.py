import pathlib
import bpy

import common
import eu07_tools

def create_material(name):
    bl_material = bpy.data.materials.new(name)
    bl_material.eu07_material.configure()
    return bl_material.eu07_material

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
    if material is None:
        return "none"

    if material.eu07_properties.is_imported:
        return str(pathlib.Path(material.eu07_properties.source_path).with_suffix(""))
    else:
        wrapper = MaterialWrapper(material)
        image = wrapper.get_diffusemap()
        if image:
            return eu07_tools.utils.shorten_asset_path(image.filepath)
        else:
            return "none"


def get_filename_from_material(material):
    if material is None:
        return "none"

    if material.eu07_properties.is_imported:
        return str(pathlib.Path(material.eu07_properties.source_path).with_suffix("").stem)
    else:
        wrapper = MaterialWrapper(material)
        image = wrapper.get_diffusemap()
        if image:
            return pathlib.Path(image.filepath).stem
        else:
            return "none"

def clean_nodegroups():
    ng_names = [
        MATERIAL_BLOCK_NAME,
        RANDOM_TEXTURESET_NAME
    ]

    for ng_name in ng_names:
        ng = bpy.data.node_groups.get(ng_name)
        if ng:
            bpy.data.node_groups.remove(ng)





