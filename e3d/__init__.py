import bpy

import icons
from e3d.input.operator import EU07_OT_ImportE3D, EU07_FH_e3d_import


classes = (
    EU07_OT_ImportE3D,
    EU07_FH_e3d_import,
)


def menu_func_import(self, context):
    self.layout.operator(
        EU07_OT_ImportE3D.bl_idname, text="[EU07] Binary Model (.e3d)",
        icon_value=icons.get_icon_id("sz_icon")
    )


def menu_func_export(self, context):
    pass
    #self.layout.operator(E3DExport.bl_idname, text="[EU07] Binary Model (.e3d)")


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