from . import matblock, material, randomtextureset, texture

modules = (
    matblock,
    material,
    randomtextureset,
    texture
)


def register():
    for mod in modules:
        mod.register()


def unregister():
    for mod in modules:
        mod.unregister()