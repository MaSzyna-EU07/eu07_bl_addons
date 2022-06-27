from . import entity
from . import geometry
from . import ui

def register():
    entity.register()
    geometry.register()
    ui.register()

def unregister():
    entity.unregister()
    geometry.unregister()
    ui.unregister()
