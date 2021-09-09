bl_info = {
    "name": "EU07 Train Simulator modeling tools",
    "description": "Editing tools for EU07 Train Simulator assets",
    "author": "Balaclava vel krzysiuup",
    "version": (0, 0, 0),
    "blender": (2, 80, 0),
    "category": "Import/Export"
}

import sys, os
sys.path.append(os.path.dirname(__file__))

from . import t3d
from . import e3d
from . import scn
from . import mat
from . import preferences



# def menu_materialslot(self, context):
#     self.layout.operator(CopyMaterialsToSelectedOperator.bl_idname, text="Copy To Selected")


def register():
    preferences.register()
    t3d.register()
    e3d.register()
    scn.register()
    mat.register()


def unregister():
    preferences.unregister()
    t3d.unregister()
    e3d.unregister()
    scn.unregister()
    mat.unregister()


if __name__ == "__main__":
    register()