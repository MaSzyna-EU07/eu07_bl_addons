import bpy

import icons
from .input import INCImportOperator

classes = (
    INCImportOperator,
)


def menu_func_import(self, context):
    self.layout.operator(
        INCImportOperator.bl_idname, text="[EU07] Scenery INC (.inc)",
        icon_value=icons.get_icon_id("sz_icon")
    )


def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)






            

