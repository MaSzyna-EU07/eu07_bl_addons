import bpy
from bpy.props import PointerProperty

from .input_builders import SCNImport
from .output_builders import SCNExport
from .basemaps import BasemapPanel, LoadBasemapOperator, BasemapProperties
from .scenery_object import SCNObjectProperties, SCNObjectPropertiesPanel, CopyMaterialsToSelectedOperator


classes = (
    SCNImport,
    SCNExport,

    BasemapProperties,
    BasemapPanel,
    LoadBasemapOperator,

    SCNObjectProperties,
    SCNObjectPropertiesPanel,
    CopyMaterialsToSelectedOperator
)


def menu_func_import(self, context):
    self.layout.operator(SCNImport.bl_idname, text="[EU07] Scenery File (.scn, .scm)")


def menu_func_export(self, context):
    self.layout.operator(SCNExport.bl_idname, text="[EU07] Scenery File (.scn, .scm)")


def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.Object.scn_properties = PointerProperty(type=SCNObjectProperties)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)