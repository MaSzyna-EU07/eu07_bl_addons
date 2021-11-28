import pathlib
import subprocess

import eu07_tools

from .utils import get_root
from .preferences import get_preferences

import os


def run_model_preview(model_abspath):
    root = get_root()
    model_relpath = eu07_tools.utils.shorten_asset_path(model_abspath)

    scn_elements = []

    node_model = eu07_tools.scn.create_element("node:model")
    node_model.path = model_relpath
    scn_elements.append(node_model)

    preview_args = get_preferences().preview_command.split(" ")
    scn_arg = "blender_export_preview.scn"
    for i, arg in enumerate(preview_args):
        if arg.endswith(".exe"):
            preview_args[i] = str(pathlib.Path(root, arg))
            break
        if arg.endswith(".scn"):
            scn_arg = arg

    scn_path = pathlib.Path(root, "scenery", scn_arg)
    with open(scn_path, "w", encoding="windows-1250", newline="\r\n") as outfile:
        outfile.write("//$a\n")
        eu07_tools.scn.dump(scn_elements, outfile)

    cwd = os.getcwd()
    os.chdir(root)
    subprocess.run(preview_args)
    os.chdir(cwd)