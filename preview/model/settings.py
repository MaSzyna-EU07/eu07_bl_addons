import bpy


class ModelPreviewSettings(bpy.types.PropertyGroup):
    executable_command: bpy.props.StringProperty(
        default="eu07.exe"
    )

    angles: bpy.props.FloatVectorProperty(
        size=3,
        default=(0, 0, 0)
    )

    use_skins: bpy.props.BoolProperty(
        name="Use skins",
        default=True
    )

    lights: bpy.props.StringProperty(
        name="Light states",
        default=""
    )

    lightcolors: bpy.props.StringProperty(
        name="Light colors",
        default=""
    )

    transition: bpy.props.BoolProperty(
        name="Light transition",
        default=True
    )

    use_ground: bpy.props.BoolProperty(
        name="Use ground",
        default=True
    )

    use_track: bpy.props.BoolProperty(
        name="Use track",
        default=False,
    )


def register():
    bpy.utils.register_class(ModelPreviewSettings)
    bpy.types.Scene.eu07_model_preview = bpy.props.PointerProperty(type=ModelPreviewSettings)


def unregister():
    bpy.utils.unregister_class(ModelPreviewSettings)
    del bpy.types.Scene.eu07_model_preview