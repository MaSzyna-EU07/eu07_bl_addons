bl_info = {
    "name": "'MaSzyna' Train Simulator developer tools",
    "description": "Tools for 'MaSzyna' Train Simulator assets - models, scenes, materials",
    "author": "Balaclava vel krzysiuup - based on firleju's work",
    "version": (2022, 2, 1),
    "blender": (3, 0, 0),
    "category": "Import/Export"
}

import sys, os
sys.path.append(os.path.dirname(__file__))

from . import common, t3d, e3d, scn, material_tools, project, preview


def register():
    common.register()
    project.register()
    t3d.register()
    e3d.register()
    scn.register()
    material_tools.register()
    preview.register()


def unregister():
    common.unregister()
    project.register()
    t3d.unregister()
    e3d.unregister()
    scn.unregister()
    material_tools.unregister()
    preview.unregister()


if __name__ == "__main__":
    register()