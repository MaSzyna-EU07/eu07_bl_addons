from . import matblock, material, randomtextureset, texture, shader_inputs_map

modules = (
    matblock,
    material,
    randomtextureset,
    texture,
    shader_inputs_map
)


def register():
    for mod in modules:
        mod.register()


def unregister():
    for mod in modules:
        mod.unregister()