from . import utils
from . import input as input_
from . import panel
from . import skins
from . import structures
from . import output
from .nodegroups import ops
from . import opacity_flag

modules = (
    input_,
    skins,
    structures,
    panel,
    output,
    ops,
    opacity_flag
)


def register():
    for mod in modules:
        mod.register()


def unregister():
    for mod in modules:
        mod.unregister()





