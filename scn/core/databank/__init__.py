from . import railprofile
from . import model

def register():
    railprofile.register()
    model.register()

def unregister():
    railprofile.unregister()
    model.unregister()