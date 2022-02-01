from . import utils
from . import input as input_
from . import panel
from . import skins
from . import properties


def register():
    properties.register()
    input_.register()
    skins.register()
    panel.register()


def unregister():
    input_.unregister()
    skins.unregister()
    panel.unregister()
    properties.unregister()





