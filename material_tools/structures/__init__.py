from . import matblock, material, randomset, texture

modules = (
    matblock,
    material,
    randomset,
    texture
)


def register():
    for mod in modules:
        mod.register()


def unregister():
    for mod in modules:
        mod.unregister