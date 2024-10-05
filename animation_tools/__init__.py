import bpy

import icons
from .output import EU07_OT_ExportAnimation

classes = (
    EU07_OT_ExportAnimation,
)


def menu_func_export(self, context):
    self.layout.operator(
        EU07_OT_ExportAnimation.bl_idname, text="[EU07] Animation as Events (.ctr)",
        icon_value=icons.get_icon_id("sz_icon")
    )


def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)








