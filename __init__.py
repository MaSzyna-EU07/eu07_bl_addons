bl_info = {
    "name": "EU07 Train Simulator modeling tools",
    "description": "Editing tools for EU07 Train Simulator assets",
    "author": "Balaclava vel krzysiuup",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "category": "Import/Export"
}

import sys, os
sys.path.append(os.path.dirname(__file__))

import bpy
from bpy.props import PointerProperty, StringProperty

from .scn import SCNImport, SCNExport, SCNObjectProperties, SCNObjectPropertiesPanel, LoadBasemapOperator, EU07SceneryProperties, LoadBasemapPanel, CopyMaterialsToSelectedOperator, UpdateTrajectoryProfileOperator
from .mat import EU07MaterialImporter
from .e3d import E3DImport
from .common import EU07UtilsPanel

from . import t3d

class EU07AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    root: StringProperty(
        name="Root path",
        subtype='FILE_PATH'
    )

    def draw(self, context):
        self.layout.prop(self, "root")




def menu_func_import(self, context):
    self.layout.operator(E3DImport.bl_idname, text="[EU07] Binary Model (.e3d)")
    self.layout.operator(SCNImport.bl_idname, text="[EU07] Scenery File (.scn, .scm)")
    self.layout.operator(EU07MaterialImporter.bl_idname, text="[EU07] Material (.mat)")



def menu_func_export(self, context):
    self.layout.operator(SCNExport.bl_idname, text="[EU07] Scenery File (.scn, .scm)")
    #self.layout.operator(MATExport.bl_idname, text="EU07 Material (.mat)")

def menu_materialslot(self, context):
    self.layout.operator(CopyMaterialsToSelectedOperator.bl_idname, text="Copy To Selected")

classes = (
    EU07AddonPreferences,
    EU07MaterialImporter,
    SCNImport,
    SCNExport,
    SCNObjectProperties,
    SCNObjectPropertiesPanel,
    LoadBasemapOperator,
    LoadBasemapPanel,
    EU07SceneryProperties,
    E3DImport,
    CopyMaterialsToSelectedOperator,
    EU07UtilsPanel,
    UpdateTrajectoryProfileOperator
)


def register():
    t3d.register()
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.Object.scn_properties = PointerProperty(type=SCNObjectProperties)
    bpy.types.Scene.eu07_properties = PointerProperty(type=EU07SceneryProperties)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    t3d.unregister()
    for c in classes:
        bpy.utils.unregister_class(c)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    
if __name__ == "__main__":
    register()