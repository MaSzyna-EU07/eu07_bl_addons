import bpy

from mat.material_wrapper import MaterialWrapper


class EU07_OT_ApplyWeatherPreview(bpy.types.Operator):
    bl_idname = "eu07.apply_weather_preview"
    bl_label = "Apply"

    def execute(self, context):
        for material in bpy.data.materials:
            material_wrapper = MaterialWrapper(material)
            variant_block = self._get_variant_block(material_wrapper)
            variant_block.make_active()

        return {'FINISHED'}


    def _get_variant_block(self, material_wrapper):
        season = bpy.context.scene.scn_season
        weather = bpy.context.scene.scn_weather

        main_block = material_wrapper.get_main_block()

        season_block = main_block.get_sub_block(season)
        if season_block:
            weather_block = season_block.get_sub_block(weather)
            if weather_block:
                return weather_block
            else:
                main_weather_block = main_block.get_sub_block(weather)
                if main_weather_block:
                    return main_weather_block

            return season_block
        else:
            return main_block


def update_weather_preview(self, context):
    bpy.ops.eu07.apply_weather_preview()


class EU07_PT_WeatherPreview(bpy.types.Panel):
    bl_idname = "EU07_PT_WeatherPreview"
    bl_label = "Weather Preview"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "[EU07] Toolbox"

    def draw(self, context):
        season_row = self.layout.row()
        season_row.prop(bpy.context.scene, "scn_season")
        weather_row = self.layout.row()
        weather_row.prop(bpy.context.scene, "scn_weather")


classes = (
    EU07_PT_WeatherPreview,
    EU07_OT_ApplyWeatherPreview,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.scn_season = bpy.props.EnumProperty(
        name="Season",
        items=[
            ("undefined", "-", ""),
            ("spring", "Spring", ""),
            ("summer", "Summer", ""),
            ("autumn", "Autumn", ""),
            ("winter", "Winter", ""),
        ],
        update=update_weather_preview
    )
    bpy.types.Scene.scn_weather = bpy.props.EnumProperty(
        name="Weather",
        items=[
            ("undefined", "-", ""),
            ("clear", "Clear", ""),
            ("cloudy", "Cloudy", ""),
            ("rain", "Rain", ""),
            ("snow", "Snow", ""),
        ],
        update=update_weather_preview
    )


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
