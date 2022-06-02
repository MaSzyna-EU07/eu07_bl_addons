import bpy

from scn.entity.node import NodeProperties


class ModelLightProperties(bpy.types.PropertyGroup):
    state: bpy.props.FloatProperty(
        name="State",
        min=0,
        max=5,
        default=0,
    )


class ModelLightColorProperties(bpy.types.PropertyGroup):
    hex_color: bpy.props.StringProperty(
        name="Hex color",
        default="-1"
    )


class ModelProperties(NodeProperties):
    name: bpy.props.StringProperty(
        name="Name",
        default="model",
        get=None,
        set=None,
    )

    location: bpy.props.FloatVectorProperty(
        name="Location",
        get=None,
        set=None,
    )

    rotation: bpy.props.FloatVectorProperty(
        name="Rotation",
        get=None,
        set=None,
    )

    model_path: bpy.props.StringProperty(
        name="Asset path",
        get=None,
        set=None,
        update=None,
        subtype="FILE_PATH"
    )

    replacableskin_path: bpy.props.StringProperty(
        name="Replacableskin path",
        get=None,
        set=None,
        update=None,
        subtype="FILE_PATH"
    )

    lights: bpy.props.CollectionProperty(
        type=ModelLightProperties,
        name="Lights",
    )

    lightcolors: bpy.props.CollectionProperty(
        type=ModelLightColorProperties,
        name="Lightcolors",
    )

    notransition: bpy.props.BoolProperty(
        name="NoTransition",
    )


classes = (
    ModelLightProperties,
    ModelLightColorProperties,
    ModelProperties,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.eu07_model = bpy.props.PointerProperty(type=ModelProperties)


def unregister():
    for cls in classes:
        bpy.utils.register_class(cls)