import bpy

from . import callbacks
from .....scn.core.entity.node import NodeProperties


class LinesProperties(NodeProperties):
    color: bpy.props.FloatVectorProperty(
        name="Color",
        size=3,
        default=[0,0,0],
        subtype='COLOR',
        min=0,
        max=1,
        # get=callbacks.get_color,
        # set=callbacks.set_color,
    )

    thickness: bpy.props.FloatProperty(
        name="Thickness",
        default=0.1,
        unit='LENGTH',
        min=0,
        max=0.25,
        # get=callbacks.get_thickness,
        # set=callbacks.set_thickness
    )


classes = (
    LinesProperties,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.eu07_scn_lines = bpy.props.PointerProperty(type=LinesProperties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.eu07_scn_lines