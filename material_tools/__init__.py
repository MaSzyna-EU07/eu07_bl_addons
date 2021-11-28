import bpy

from . import utils
from .input import EU07_OT_MaterialImport
from .panel import EU07_PT_MaterialToolsPanel
from .nodegroup import delete_mat_nodegroup_template, create_mat_nodegroup_template

classes = (
    EU07_PT_MaterialToolsPanel,
    EU07_OT_MaterialImport,
)


def menu_func_import(self, context):
    self.layout.operator(EU07_OT_MaterialImport.bl_idname, text="[EU07] Material (.mat)")


def menu_func_export(self, context):
    pass
    #self.layout.operator(MATExport.bl_idname, text="EU07 Material (.mat)")


def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


