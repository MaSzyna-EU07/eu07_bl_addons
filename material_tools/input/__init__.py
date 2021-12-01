import bpy

from .operator import EU07_OT_MaterialImport
from .importer import MATImporter


classes = (
    EU07_OT_MaterialImport,
)


def menu_func_import(self, context):
    self.layout.operator(EU07_OT_MaterialImport.bl_idname, text="[EU07] Material (.mat)")


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)