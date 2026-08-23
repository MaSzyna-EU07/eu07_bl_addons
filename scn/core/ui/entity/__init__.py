import bpy

from .panel import SCN_PT_entity

classes = (
    SCN_PT_entity,
)

def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
