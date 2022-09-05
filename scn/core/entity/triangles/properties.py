import bpy

from scn.core.entity.node import NodeProperties


class TrianglesProperties(NodeProperties):
    pass


classes = (
    TrianglesProperties,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.eu07_scn_triangles = bpy.props.PointerProperty(type=TrianglesProperties)


def unregister():
    for cls in classes:
        bpy.utils.register_class(cls)