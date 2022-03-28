import bpy


class NodeProperties(bpy.types.PropertyGroup):
    max_distance: bpy.props.FloatProperty(
        name="Max Distance",
        default=-1,
        unit="LENGTH",
    )

    min_distance: bpy.props.FloatProperty(
        name="Min Distance",
        default=-1,
        unit="LENGTH",
    )

    name: bpy.props.StringProperty(
        name="Name",
        get=None,
        set=None,
    )