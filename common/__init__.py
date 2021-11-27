from .utils import *
from . import includes
from . import preferences
from . import weather
from . import level_of_detail


def register():
    includes.register()
    preferences.register()
    weather.register()
    level_of_detail.register()


def unregister():
    includes.unregister()
    preferences.unregister()
    weather.unregister()
    level_of_detail.unregister()





