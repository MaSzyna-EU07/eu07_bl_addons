import bpy


classes = (

)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.scn_season = bpy.props.EnumProperty(
        name="Season",
        items=[
            ("spring", "Spring", ""),
            ("summer", "Summer", ""),
            ("autumn", "Autumn", ""),
            ("winter", "Winter", ""),
        ]
    )
    bpy.types.Scene.scn_weather = bpy.props.EnumProperty(
        name="Weather",
        items=[
            ("clear", "Clear", ""),
            ("cloudy", "Cloudy", ""),
            ("rain", "Rain", ""),
            ("snow", "Snow", ""),
        ]
    )


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
