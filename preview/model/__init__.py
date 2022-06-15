import bpy

from .import ui
from . import operator
from . import settings


def register():
    operator.register()
    settings.register()


def unregister():
    operator.unregister()
    settings.unregister()