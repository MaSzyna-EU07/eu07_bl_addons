import bpy

from . import entity


def register():
    entity.register()


def unregister():
    entity.unregister()


