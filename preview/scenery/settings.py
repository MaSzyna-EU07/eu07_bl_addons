import bpy


class SceneryPreviewSettings(bpy.types.PropertyGroup):
    executable_command: bpy.props.StringProperty(
        default="eu07.exe"
    )


def register():
    bpy.utils.register_class(SceneryPreviewSettings)
    bpy.types.Scene.eu07_scenery_preview = bpy.props.PointerProperty(type=SceneryPreviewSettings)


def unregister():
    del bpy.types.Scene.eu07_scenery_preview