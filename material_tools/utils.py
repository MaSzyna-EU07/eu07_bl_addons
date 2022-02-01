import pathlib

import common


def get_qualified_material_name(abspath, opacity=1):
    root = common.utils.get_environment_path()

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

    shortpath = material.eu07_properties.source_path

    if shortpath == "":
        return "none"

    return shortpath