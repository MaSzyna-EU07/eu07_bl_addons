from . import properties
from . import panel


def register():
    properties.register()
    panel.register()


def unregister():
    properties.unregister()
    panel.unregister()



