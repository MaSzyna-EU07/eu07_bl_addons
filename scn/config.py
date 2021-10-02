import bpy

import eu07_tools

def get_active_setting():
    if bpy.context.scene.scn_config:
        return bpy.context.scene.scn_config[bpy.context.scene.scn_config_setting_index]

    return None


def get_config_as_element():
    element = eu07_tools.scn.create_element("config")

    element.content = "\n".join(
        (f"{setting.key} {setting.value}" for setting in bpy.context.scene.scn_config)
    )

    return element


def set_config_from_element(element):
    pass


class SCNConfig(bpy.types.PropertyGroup):
    key: bpy.props.StringProperty(
        name="Key",
    )

    value: bpy.props.StringProperty(
        name="Value"
    )


class SCN_UL_SceneryConfig(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'PREFERENCES'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=f"{item.key}", icon=custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon=custom_icon)


class SCN_PT_SceneryConfig(bpy.types.Panel):
    bl_idname = "SCN_PT_scn_config"
    bl_label = "SCN Config"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "[EU07] SCN Editor"

    def draw(self, context):
        list_row = self.layout.row()
        list_row.template_list("SCN_UL_SceneryConfig", "", bpy.context.scene, "scn_config", bpy.context.scene, "scn_config_setting_index")

        operators_row = self.layout.row()
        operators_row.operator("scn.add_config_setting", text="Add")
        operators_row.operator("scn.delete_config_setting", text="Remove")

        item = get_active_setting()

        if item:
            name_row = self.layout.row()
            name_row.prop(item, "key")

            value_row = self.layout.row()
            value_row.prop(item, "value")


class SCN_OT_AddConfigSetting(bpy.types.Operator):
    bl_idname = "scn.add_config_setting"
    bl_label = "Add new setting to config"

    def execute(self, context):
        added = bpy.context.scene.scn_config.add()
        context.scene.scn_config_setting_index = len(context.scene.scn_config) - 1

        return {'FINISHED'}

class SCN_OT_DeleteConfigSetting(bpy.types.Operator):
    bl_idname = "scn.delete_config_setting"
    bl_label = "Delete setting from config"

    @classmethod
    def poll(cls, context):
        return context.scene.scm_files

    def execute(self, context):
        config = context.scene.scn_config
        setting_index = context.scene.scn_config_setting_index

        config.remove(setting_index)
        context.scene.scn_config_setting_index = min(max(0, setting_index - 1), len(config) - 1)

        return {'FINISHED'}

