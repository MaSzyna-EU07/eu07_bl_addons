import bpy


class EU07MaterialProperties(bpy.types.PropertyGroup):
    source_path = bpy.props.StringProperty(
        name="Source path",
    )