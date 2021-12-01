from .utils import *
from . import includes
from . import preferences
from . import weather
from . import model_preview


def register():
    includes.register()
    preferences.register()
    weather.register()
    model_preview.register()


def unregister():
    includes.unregister()
    preferences.unregister()
    weather.unregister()
    model_preview.unregister()





