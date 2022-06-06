import bpy


class RailProfilePoint(bpy.types.PropertyGroup):
    position: bpy.props.FloatVectorProperty(
        size=2,
    )

    normal: bpy.props.FloatVectorProperty(
        size=2,
    )

    mapping: bpy.props.FloatProperty()


class RailProfile(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()

    points_rail: bpy.props.CollectionProperty(
        type=RailProfilePoint
    )

    points_blade: bpy.props.CollectionProperty(
        type=RailProfilePoint
    )


class RailProfileBank(bpy.types.PropertyGroup):
    profiles: bpy.props.CollectionProperty(
        type=RailProfile
    )