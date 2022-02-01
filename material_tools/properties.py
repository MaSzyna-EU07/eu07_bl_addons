import bpy


class EU07MaterialProperties(bpy.types.PropertyGroup):
    source_path: bpy.props.StringProperty(
        name="Source path",
        subtype='FILE_PATH',
        description="Source path for this material, relative to environment root."
    )


classes = (
    EU07MaterialProperties,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Material.eu07_properties = bpy.props.PointerProperty(type=EU07MaterialProperties)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)