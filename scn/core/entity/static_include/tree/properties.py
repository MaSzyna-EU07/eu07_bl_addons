import bpy

class StaticInclude_TreeProperties(bpy.types.PropertyGroup):
    skin: bpy.props.PointerProperty(
        name="Skin",
        type=bpy.types.Material
    )

    location: bpy.props.FloatVectorProperty(
        name="Location",
        get=None,
        set=None,
    )

    rotation: bpy.props.FloatProperty(
        name="Rotation",
        get=None,
        set=None
    )

    height: bpy.props.FloatProperty(
        name="Height",
        min=0,
        get=None,
        set=None,
    )

    span: bpy.props.FloatProperty(
        name="Span",
        min=0,
        get=None,
        set=None,
    )


def register():
    bpy.utils.register_class(StaticInclude_TreeProperties)
    bpy.types.Object.eu07_scn_staticinc_tree = bpy.props.PointerProperty(
        type=StaticInclude_TreeProperties
    )


def unregister():
    bpy.utils.unregister_class(StaticInclude_TreeProperties)
    del bpy.types.Object.eu07_staticinc_tree