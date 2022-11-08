bl_info = {
    "filename": "'MaSzyna' Train Simulator developer tools",
    "description": "Tools for 'MaSzyna' Train Simulator assets - models, scenes, materials",
    "author": "Balaclava vel krzysiuup - based on firleju's work",
    "version": (2022, 2, 1),
    "blender": (3, 0, 0),
    "category": "Import/Export"
}

import sys, os
sys.path.append(os.path.dirname(__file__))

from . import common, t3d, e3d, scn, material_tools, project, preview, animation_tools, inc


modules = (
    common,
    project,
    t3d,
    e3d,
    scn,
    material_tools,
    animation_tools,
    preview,
    inc
)

def register():
    for mod in modules:
        mod.register()


def unregister():
    for mod in modules:
        mod.unregister()


if __name__ == "__main__":
    register()