from .utils import *
from . import includes
from . import preferences
from . import weather


def register():
    includes.register()
    preferences.register()
    weather.register()


def unregister():
    includes.unregister()
    preferences.unregister()
    weather.unregister()





