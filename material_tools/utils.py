import pathlib
import bpy

import common
import eu07_tools

from .wrapper import MaterialWrapper


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
        return material.eu07_properties.source_path
    else:
        wrapper = MaterialWrapper(material)
        image = wrapper.get_diffusemap()
        if image:
            return eu07_tools.utils.shorten_asset_path(image.filepath)
        else:
            return "none"




