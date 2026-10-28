import bpy
from bpy.props import PointerProperty, BoolProperty, FloatProperty

from .input import EU07_OT_ImportT3D, EU07_FH_t3d_import
from .output import EU07_OT_ExportT3D, EU07_FH_t3d_export
from .properties import (
    T3DSubmodelProperties, T3DSubmodelPropertiesPanel, EU07_OT_FreeSpotLightToSimulator, EU07_OT_FreeSpotLightShadeSelf,
    get_freespot_intensity, set_freespot_intensity
)
from . import sim_light
from .. import icons

classes = (
    EU07_OT_ImportT3D,
    EU07_FH_t3d_import,
    EU07_OT_ExportT3D,
    EU07_FH_t3d_export,
    T3DSubmodelProperties,
    EU07_OT_FreeSpotLightToSimulator,
    EU07_OT_FreeSpotLightShadeSelf,
    T3DSubmodelPropertiesPanel
)


def menu_func_import(self, context):
    icons.get_icons()
    self.layout.operator(
        EU07_OT_ImportT3D.bl_idname, text="[EU07] Text Model (.t3d)",
        icon_value=icons.get_icon_id("sz_icon")
    )


def menu_func_export(self, context):
    icons.get_icons()
    self.layout.operator(
        EU07_OT_ExportT3D.bl_idname, text="[EU07] Text Model (.t3d)",
        icon_value=icons.get_icon_id("sz_icon")
    )


def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.Object.t3d_properties = PointerProperty(type=T3DSubmodelProperties)
    bpy.types.Light.eu07_simulator_light = BoolProperty(
        name="Simulator Light Units",
        description=(
            "The colour, the energy and the blend of the spot light are in the units of the simulator "
            "(Diffuse^2.2, HotspotPower, the cosines of the cones), and its radius, falloff and shadows go to the model. "
            "A point light in the units is a point light of the simulator (FalloffAngle 360), not a point of stars. "
            "Lights made before go to the model as they are"
        ),
        default=False,
    )
    bpy.types.Scene.eu07_freespot_intensity = FloatProperty(
        name="Light Point Brightness",
        description=(
            "gfx.lights.freespot.intensity of the simulator: brightness of the light points of the models. The lights "
            "in the units of the simulator keep their HotspotPower when it changes"
        ),
        min=0.001,
        soft_max=50,
        get=get_freespot_intensity,
        set=set_freespot_intensity,
    )

    bpy.app.handlers.depsgraph_update_post.append(sim_light.on_depsgraph_update)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    if sim_light.on_depsgraph_update in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(sim_light.on_depsgraph_update)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

    del bpy.types.Scene.eu07_freespot_intensity
    del bpy.types.Light.eu07_simulator_light
    del bpy.types.Object.t3d_properties

    for c in reversed(classes):
        bpy.utils.unregister_class(c)






            

