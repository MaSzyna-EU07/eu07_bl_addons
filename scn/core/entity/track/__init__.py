from . import properties
from . import railprofile

def register():
    railprofile.register()
    properties.register()


def unregister():
    railprofile.unregister()
    properties.unregister()