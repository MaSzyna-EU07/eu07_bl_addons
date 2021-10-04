from . import includes
from . import preferences
from common.utils import *

def register():
    includes.register()
    preferences.register()


def unregister():
    includes.unregister()
    preferences.unregister()


# TODO: Move this stuff to better places




