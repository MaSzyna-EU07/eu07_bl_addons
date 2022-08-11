import bpy

class StaticInclude_PlaceholderProperties(bpy.types.PropertyGroup):
    params_text: bpy.props.StringProperty(
        name="Parameters text",
    )


def register():
    bpy.utils.register_class(StaticInclude_PlaceholderProperties)
    bpy.types.Object.eu07_scn_staticinc_placeholder = bpy.props.PointerProperty(
        type=StaticInclude_PlaceholderProperties
    )


def unregister():
    bpy.utils.unregister_class(StaticInclude_PlaceholderProperties)
    del bpy.types.Object.eu07_scn_staticinc_placeholder