import bpy

from .wrapper import MaterialWrapper

class EU07MaterialProperties(bpy.types.PropertyGroup):
    source_path: bpy.props.StringProperty(
        name="Source path",
        subtype='FILE_PATH',
        description="Source path for this material, relative to environment root."
    )

    is_imported: bpy.props.BoolProperty(
        name="Is imported",
        default=False,
        description="This material was imported by addon?"
    )

classes = (
    EU07MaterialProperties,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Material.eu07_properties = bpy.props.PointerProperty(type=EU07MaterialProperties)


def unregister():
    del bpy.types.Material.eu07_properties

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)