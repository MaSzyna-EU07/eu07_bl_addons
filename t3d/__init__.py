import bpy
from bpy.props import PointerProperty

from .input import EU07_OT_ImportT3D, EU07_FH_t3d_import
from .output import EU07_OT_ExportT3D, EU07_FH_t3d_export
from .properties import T3DSubmodelProperties, T3DSubmodelPropertiesPanel

classes = (
    EU07_OT_ImportT3D,
    EU07_FH_t3d_import,
    EU07_OT_ExportT3D,
    EU07_FH_t3d_export,
    T3DSubmodelProperties,
    T3DSubmodelPropertiesPanel
)


def menu_func_import(self, context):
    self.layout.operator(EU07_OT_ImportT3D.bl_idname, text="[EU07] Text Model (.t3d)")


def menu_func_export(self, context):
    self.layout.operator(EU07_OT_ExportT3D.bl_idname, text="[EU07] Text Model (.t3d)")


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






            

