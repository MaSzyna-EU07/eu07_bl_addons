import bpy
from bpy.props import PointerProperty

from .input import T3DImportOperator
from .output import T3DExportOperator
from .properties import T3DSubmodelProperties, T3DSubmodelPropertiesPanel

classes = (
    T3DImportOperator,
    T3DExportOperator,
    T3DSubmodelProperties,
    T3DSubmodelPropertiesPanel
)


def menu_func_import(self, context):
    self.layout.operator(T3DImportOperator.bl_idname, text="[EU07] Text Model (.t3d)")


def menu_func_export(self, context):
    self.layout.operator(T3DExportOperator.bl_idname, text="[EU07] Text Model (.t3d)")


def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.Object.t3d_properties = PointerProperty(type=T3DSubmodelProperties)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)






            

