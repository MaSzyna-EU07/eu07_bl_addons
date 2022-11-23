from . import matblock, material, randomtextureset, texture, shader_inputs_data

modules = (
    matblock,
    material,
    randomtextureset,
    texture,
    shader_inputs_data
)


def register():
    for mod in modules:
        mod.register()


def unregister():
    for mod in modules:
        mod.unregister()