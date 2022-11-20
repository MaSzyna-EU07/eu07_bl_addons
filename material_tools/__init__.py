from . import utils
from . import input as input_
from . import panel
from . import skins
from . import structures
from . import output
from . import ng_ops

modules = (
    input_,
    skins,
    structures,
    panel,
    output,
    ng_ops,
)


def register():
    for mod in modules:
        mod.register()


def unregister():
    for mod in modules:
        mod.unregister()





