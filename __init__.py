bl_info = {
    "name": "EU07 Train Simulator modeling tools",
    "description": "Editing tools for EU07 Train Simulator assets",
    "author": "Balaclava vel krzysiuup",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "category": "Import/Export"
}

import bpy
from bpy.props import PointerProperty

from .t3d import T3DExport, T3DImport, T3DSubmodelProperties, T3DSubmodelPropertiesPanel

def menu_func_import(self, context):
    self.layout.operator(T3DImport.bl_idname, text="T3D Text Model (.t3d)")


# def menu_func_export(self, context):
#    self.layout.operator(ExportT3D.bl_idname, text="T3D Text Model (.t3d)")

classes = (
        T3DExport,
        T3DImport,
        T3DSubmodelProperties,
        T3DSubmodelPropertiesPanel
)

def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.Object.t3d_properties = PointerProperty(type=T3DSubmodelProperties)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

    
if __name__ == "__main__":
    register()