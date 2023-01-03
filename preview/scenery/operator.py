import math
import os
import pathlib
import subprocess

import bpy

from common import get_environment_path
from preview.common import SCENERY_FILENAME, create_camera_from_viewport, run_preview_command, SUBDIR_NAME
import eu07_tools


class EU07_OT_GameEnginePreviewScenery(bpy.types.Operator):
    bl_idname = "eu07.scenery_preview"
    bl_label = "Preview model in MaSzyna"

    def execute(self, context):
        settings = bpy.context.scene.eu07_scenery_preview

        root = get_environment_path()
        scenery_subdir = pathlib.Path(root, "scenery", SUBDIR_NAME)

        scenery_outpath = str(pathlib.Path(scenery_subdir, SCENERY_FILENAME))
        bpy.ops.export_scene.scn(filepath=scenery_outpath)

        with open(scenery_outpath, encoding="windows-1250", mode="a") as outfile:
            camera = create_camera_from_viewport()

            sky = eu07_tools.scn.create_element("sky")
            sky.model_path = "skydome_clouds.t3d"

            eu07_tools.scn.dump([camera, sky], outfile)

        run_preview_command(root, settings.executable_command)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(EU07_OT_GameEnginePreviewScenery)


def unregister():
    bpy.utils.unregister_class(EU07_OT_GameEnginePreviewScenery)