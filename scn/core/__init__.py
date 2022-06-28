from . import entity
from . import geometry
from . import ui
from . import databank

def register():
    entity.register()
    geometry.register()
    ui.register()
    databank.register()

def unregister():
    entity.unregister()
    geometry.unregister()
    ui.unregister()
    databank.unregister()