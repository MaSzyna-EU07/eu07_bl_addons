from . import utils
from . import input as input_
from . import panel
from . import skins
from .nodegroup import delete_mat_nodegroup_template, create_mat_nodegroup_template


def register():
    input_.register()
    skins.register()
    panel.register()


def unregister():
    input_.unregister()
    skins.unregister()
    panel.unregister()





