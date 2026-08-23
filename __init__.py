from . import common, t3d, e3d, scn, material_tools, project, preview, animation_tools, inc, presets, icons


modules = (
    icons,
    common,
    project,
    t3d,
    e3d,
    #scn,
    material_tools,
    animation_tools,
    preview,
    #inc,
    presets,
)


def register():
    for mod in modules:
        mod.register()


def unregister():
    for mod in reversed(modules):
        mod.unregister()


if __name__ == "__main__":
    register()