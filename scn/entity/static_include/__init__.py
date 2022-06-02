import bpy
from . import properties

def register():
    properties.register()


def unregister():
    properties.unregister()