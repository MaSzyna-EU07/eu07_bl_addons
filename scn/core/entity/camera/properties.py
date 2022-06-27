import bpy

class CameraProperties(bpy.types.PropertyGroup):
    position: bpy.props.FloatVectorProperty(
        name="Position",
        size=3,
    )

    rotation: bpy.props.FloatVectorProperty(
        name="Rotation",
        size=3,
    )

    index: bpy.props.IntProperty(
        min=-1,
        max=9,
        default=-1
    )


classes = (
    CameraProperties,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.eu07_camera = bpy.props.PointerProperty(type=CameraProperties)


def unregister():
    for cls in classes:
        bpy.utils.register_class(cls)