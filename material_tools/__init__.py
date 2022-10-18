from . import utils
from . import input as input_
from . import panel
from . import skins
from . import structures
from . import output
from . import provide_ng

modules = (
    input_,
    skins,
    structures,
    panel,
    output,
    provide_ng,
)


def register():
    for mod in modules:
        mod.register()


def unregister():
    for mod in modules:
        mod.unregister()





