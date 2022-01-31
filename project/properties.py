import bpy


class EU07ProjectProperties(bpy.types.PropertyGroup):
    operating_mode: bpy.props.EnumProperty(
        name="Operating mode",
        description="Operating mode",
        items=[
            ("modelling", "3D Modelling", "3D model creation mode"),
            ("scenery_editor", "Scenery Editor", "Scenery editing mode")
        ],
        default="modelling",
    )

    environment_path: bpy.props.StringProperty(
        name="Environment path",
        description="Environment path for this project",
        subtype='DIR_PATH',
        update=None, # TODO: Reload assets on change?
    )


def register():
    bpy.utils.register_class(EU07ProjectProperties)
    bpy.types.Scene.eu07_project_properties = bpy.props.PointerProperty(type=EU07ProjectProperties)


def unregister():
    bpy.utils.unregister_class(EU07ProjectProperties)