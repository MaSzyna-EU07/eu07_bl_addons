from . import properties
from . import placeholder
from . import tree

def register():
    properties.register()
    placeholder.register()
    tree.register()


def unregister():
    properties.unregister()
    placeholder.unregister()
    tree.unregister()