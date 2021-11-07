from . import includes
from . import preferences
from . import weather
from common.utils import *


def register():
    includes.register()
    preferences.register()
    weather.register()


def unregister():
    includes.unregister()
    preferences.unregister()
    weather.register()





