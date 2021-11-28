from .utils import *
from . import includes
from . import preferences
from . import weather
from . import level_of_detail
from . import model_preview


def register():
    includes.register()
    preferences.register()
    weather.register()
    level_of_detail.register()
    model_preview.register()


def unregister():
    includes.unregister()
    preferences.unregister()
    weather.unregister()
    level_of_detail.unregister()
    model_preview.unregister()





