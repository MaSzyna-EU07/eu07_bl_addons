import math
import pathlib
import os
import subprocess

import eu07_tools
import bpy

from .utils import get_root, get_viewport_camera_location, get_viewport_camera_rotation
from .preferences import get_preferences

from scn.camera import compensate_camera_angles


MODEL_FILENAME = "blender_preview.t3d"
SCENERY_FILENAME = "blender_preview.scn"


class EU07_OT_ModelPreview(bpy.types.Operator):
    bl_idname = "eu07.model_preview"
    bl_label = "Preview model in MaSzyna"

    def execute(self, context):
        settings = bpy.context.scene.eu07_model_preview

        root = get_root()

        model_outpath = str(pathlib.Path(root, "models", MODEL_FILENAME))
        # TODO: DO NOT EXPORT INCLUDES TO SEPARATE FILES - MERGE ALL INTO ONE FILE!
        bpy.ops.export_scene.t3d(filepath=model_outpath)

        scn_elements = []

        node_model = eu07_tools.scn.create_element("node:model")
        node_model.path = MODEL_FILENAME

        if settings.use_skins:
            pass # TODO: Write skin path

        if settings.lights:
            node_model.light_states = [float(state) for state in settings.lights.strip(" ").split(" ")]
        # TODO: Light colors
        node_model.notransition = (not settings.transition)
        node_model.rotation = eu07_tools.utils.swizzle_coords(settings.angles)

        scn_elements.append(node_model)

        camera = eu07_tools.scn.create_element("camera")

        camera.location = eu07_tools.utils.swizzle_coords(get_viewport_camera_location())

        camera_rotation = get_viewport_camera_rotation()
        degrees = [math.degrees(x) for x in camera_rotation]
        swizzled = [
            degrees[1],
            degrees[2] + 90,
            degrees[0]
        ]

        camera.rotation = swizzled

        scn_elements.append(camera)

        scn_path = pathlib.Path(root, "scenery", SCENERY_FILENAME)
        with open(scn_path, "w", encoding="windows-1250", newline="\r\n") as outfile:
            outfile.write("//$a\n")
            eu07_tools.scn.dump(scn_elements, outfile)

        cwd = os.getcwd()
        os.chdir(root)

        addon_preferences = get_preferences()
        args = [*addon_preferences.executable.split(" "), "-s", SCENERY_FILENAME]

        subprocess.Popen(args)

        os.chdir(cwd)

        return {'FINISHED'}


class ModelPreviewSettings(bpy.types.PropertyGroup):
    angles: bpy.props.FloatVectorProperty(
        size=3,
        default=(0, 0, 0)
    )

    use_skins: bpy.props.BoolProperty(
        name="Use skins",
        default=True
    )

    lights: bpy.props.StringProperty(
        name="Light states",
        default=""
    )

    lightcolors: bpy.props.StringProperty(
        name="Light colors",
        default=""
    )

    transition: bpy.props.BoolProperty(
        name="Light transition",
        default=True
    )


class EU07_PT_ModelPreview(bpy.types.Panel):
    bl_idname = "EU07_PT_ModelPreview"
    bl_label = "Model Preview Settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "[EU07] Toolbox"

    def draw(self, context):
        self.layout.operator("eu07.model_preview", icon="PLAY", text="Run Preview")

        settings = bpy.context.scene.eu07_model_preview

        addon_preferences = get_preferences()

        self.layout.prop(addon_preferences, "executable")
        #self.layout.prop(settings, "use_skins")
        lightbox = self.layout.box()
        lightbox.label(text="Lights")
        lightbox.prop(settings, "lights", text="States")
        lightbox.prop(settings, "lightcolors", text="Colors")
        lightbox.prop(settings, "transition")
        self.layout.prop(settings, "angles")


classes = (
    EU07_OT_ModelPreview,
    EU07_PT_ModelPreview,
    ModelPreviewSettings,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.eu07_model_preview = bpy.props.PointerProperty(type=ModelPreviewSettings)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)