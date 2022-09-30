import bpy

from . import operator

modules = (
    operator,
)

def menu_func_export(self, context):
    self.layout.operator(operator.EU07_OT_ExportMAT.bl_idname, text="[EU07] Material (.mat)")


def register():
    for mod in modules:
        mod.register()

    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    for mod in modules:
        mod.unregister()

    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)