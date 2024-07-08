import bpy

from . import callbacks
from scn.core.entity.node import NodeProperties


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
    location: bpy.props.FloatVectorProperty(
        name="Location",
        get=callbacks.get_location,
        set=callbacks.set_location,
    )

    rotation: bpy.props.FloatVectorProperty(
        name="Rotation",
        get=callbacks.get_rotation,
        set=callbacks.set_rotation,
    )

    model_path: bpy.props.StringProperty(
        name="Asset path",
        update=callbacks.update_path,
        subtype="FILE_PATH"
    )

    replacableskin_1: bpy.props.PointerProperty(
        type=bpy.types.Material,
        name="Skin #1",
        update=callbacks.update_replacableskin_1,
    )

    replacableskin_2: bpy.props.PointerProperty(
        type=bpy.types.Material,
        name="Skin #2",
        update=callbacks.update_replacableskin_2,
    )

    replacableskin_3: bpy.props.PointerProperty(
        type=bpy.types.Material,
        name="Skin #3",
        update=callbacks.update_replacableskin_3,
    )

    replacableskin_4: bpy.props.PointerProperty(
        type=bpy.types.Material,
        name="Skin #4",
        update=callbacks.update_replacableskin_4,
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

    @property
    def replacableskin_materials(self):
        return {
            -1: self.replacableskin_1,
            -2: self.replacableskin_2,
            -3: self.replacableskin_3,
            -4: self.replacableskin_4
        }



classes = (
    ModelLightProperties,
    ModelLightColorProperties,
    ModelProperties,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.eu07_scn_model = bpy.props.PointerProperty(type=ModelProperties)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.eu07_scn_model