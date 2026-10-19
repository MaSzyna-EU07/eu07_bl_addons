import bpy

from . import core
from . import output

classes = (
)


def register():
    core.register()
    output.register()

    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    core.unregister()
    output.unregister()

    for c in reversed(classes):
        bpy.utils.unregister_class(c)