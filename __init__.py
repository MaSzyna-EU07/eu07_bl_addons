bl_info = {
    "name": "EU07 Train Simulator modeling tools",
    "description": "Editing tools for EU07 Train Simulator assets",
    "author": "Balaclava vel krzysiuup",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "category": "Import/Export"
}

import bpy
from bpy.props import PointerProperty, StringProperty

from .t3d import T3DExport, T3DImport, T3DSubmodelProperties, T3DSubmodelPropertiesPanel
from .scn import SCNImport, LoadBasemapOperator, EU07SceneryProperties, LoadBasemapPanel
from .mat import MATImport

class EU07AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    root: StringProperty(
        name="Root path",
        subtype='FILE_PATH'
    )

    def draw(self, context):
        self.layout.prop(self, "root")

def menu_func_import(self, context):
    self.layout.operator(T3DImport.bl_idname, text="T3D Text Model (.t3d)")
    self.layout.operator(SCNImport.bl_idname, text="EU07 Scenery File (.scn, .scm)")
    #self.layout.operator(MATImport.bl_idname, text="EU07 Material (.mat)")

def menu_func_export(self, context):
    self.layout.operator(T3DExport.bl_idname, text="T3D Text Model (.t3d)")
    #self.layout.operator(MATExport.bl_idname, text="EU07 Material (.mat)")

classes = (
        EU07AddonPreferences,
        T3DExport,
        T3DImport,
        T3DSubmodelProperties,
        T3DSubmodelPropertiesPanel,
        MATImport,
        SCNImport,
        LoadBasemapOperator,
        LoadBasemapPanel,
        EU07SceneryProperties
)

def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.Object.t3d_properties = PointerProperty(type=T3DSubmodelProperties)
    bpy.types.Scene.eu07_properties = PointerProperty(type=EU07SceneryProperties)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    
if __name__ == "__main__":
    register()