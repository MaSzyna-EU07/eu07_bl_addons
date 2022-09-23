from . import utils
from . import input as input_
from . import panel
from . import skins
from . import structures

modules = (
    input_,
    skins,
    panel,
    structures
)


def register():
    for mod in modules:
        mod.register()


def unregister():
    for mod in modules:
        mod.unregister()





