import bpy

from mat.nodegroup import NodeGroupWrapper


class EU07_OT_ApplyWeatherPreview(bpy.types.Operator):
    bl_idname = "eu07.apply_weather_preview"
    bl_label = "Apply"

    def execute(self, context):
        for material in bpy.data.materials:
            nodes = material.node_tree.nodes
            links = material.node_tree.links

            mat_nodegroups = [
                node for node in nodes if (
                    node.label == "[EU07] Material" and
                    node.outputs[0].links[0].to_node and node.outputs[0].links[0].to_node.label != "[EU07] Material"
                )
            ]

            print(mat_nodegroups)

            if not mat_nodegroups:
                continue

            outputs = [node for node in nodes if node.bl_idname == "ShaderNodeOutputMaterial"]
            if not outputs:
                continue

            # dirty solution
            wrapper = NodeGroupWrapper(mat_nodegroups[0], material.node_tree)
            variant_node = self._get_variant(wrapper)
            links.new(variant_node.outputs[0], outputs[0].inputs[0])

        return {'FINISHED'}


    def _get_variant(self, wrapper):
        season = bpy.context.scene.scn_season
        weather = bpy.context.scene.scn_weather

        season_wrapper = wrapper.get_nested(season)
        if season_wrapper:
            weather_wrapper = season_wrapper.get_nested(weather)
            if weather_wrapper:
                return weather_wrapper.nodegroup
            else:
                main_weather_wrapper = wrapper.get_nested(weather)
                if main_weather_wrapper:
                    return main_weather_wrapper.nodegroup

            return season_wrapper.nodegroup
        else:
            return wrapper.nodegroup


class EU07_OT_RestoreDefaultWeatherPreview(bpy.types.Operator):
    bl_idname = "eu07.restore_default_weather_preview"
    bl_label = "Restore Default"

    def execute(self, context):
        return {'FINISHED'}


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
        apply_r = self.layout.row()
        apply_r.operator("eu07.apply_weather_preview")
        restore_r = self.layout.row()
        restore_r.operator("eu07.restore_default_weather_preview")


classes = (
    EU07_PT_WeatherPreview,
    EU07_OT_ApplyWeatherPreview,
    EU07_OT_RestoreDefaultWeatherPreview
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
