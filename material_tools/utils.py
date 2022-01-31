import pathlib

import common



def get_qualified_material_name(abspath, opacity=1):
    root = common.utils.get_root(abspath)

    try:
        name = str(pathlib.Path(abspath).relative_to(root).with_suffix(""))

        if opacity == 0:
            name += "_Transparent"
        elif opacity < 1:
            name += f"_Clip({opacity})" # TODO: Check if clip and opacity are the same (scale may be opposite)

        return name
    except ValueError:
        return ""


def get_shortpath_from_material(material):
    # TODO: Implement
    return "NotImplemented"