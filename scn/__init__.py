import bpy
from bpy.props import PointerProperty, CollectionProperty, IntProperty

from .output import SCNExporter
from .input import  SCNImportOperator
from .basemaps import BasemapPanel, LoadBasemapOperator, BasemapProperties
from .scenery_object import SCNObjectProperties, SCNObjectPropertiesPanel, CopyMaterialsToSelectedOperator
from .tree_utils import AddTreeOperator
from .scenery_tools_panel import SCNToolsPanel
from .sectorizer import SCN_OT_LoadSectors
from .config import SCNConfig, SCN_PT_SceneryConfig, SCN_UL_SceneryConfig, SCN_OT_AddConfigSetting, SCN_OT_DeleteConfigSetting
from .trajectory_tools.trajectory_operators import AddTrackOperator


from . import sound
from . import camera
from . import tree_utils
from . import memcell

from . import entity
from . import ui

classes = (
    SCNImportOperator,
    SCNExporter,

    #BasemapProperties,
    #BasemapPanel,
    #LoadBasemapOperator,

    SCNToolsPanel,
    SCNObjectProperties,
    SCNObjectPropertiesPanel,
    CopyMaterialsToSelectedOperator,

    AddTreeOperator,

    AddTrackOperator,

    SCNConfig,
    SCN_PT_SceneryConfig,
    SCN_OT_AddConfigSetting,
    SCN_UL_SceneryConfig,
    SCN_OT_DeleteConfigSetting,
)


def menu_func_import(self, context):
    self.layout.operator(SCNImportOperator.bl_idname, text="[EU07] Scenery File (.scn, .scm)")


def menu_func_export(self, context):
    self.layout.operator(SCNExporter.bl_idname, text="[EU07] Scenery File (.scn, .scm)")


def register():
    sectorizer.register()
    entity.register()
    ui.register()

    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.Object.scn_properties = bpy.props.PointerProperty(type=SCNObjectProperties)

    bpy.types.Scene.scn_config = bpy.props.CollectionProperty(type=SCNConfig)
    bpy.types.Scene.scn_config_setting_index = bpy.props.IntProperty(min=0)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    sectorizer.unregister()
    entity.unregister()
    ui.unregister()

    for c in classes:
        bpy.utils.unregister_class(c)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)