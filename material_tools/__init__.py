from . import utils
from . import input as input_
from . import panel
from . import skins
from . import structures
from . import output

modules = (
    input_,
    skins,
    panel,
    structures,
    output,
)


def register():
    for mod in modules:
        mod.register()


def unregister():
    for mod in modules:
        mod.unregister()





