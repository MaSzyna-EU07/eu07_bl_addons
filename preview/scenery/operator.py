import math
import os
import pathlib
import subprocess

import bpy

import eu07_tools
from animation_tools.output.eventize import eventize_object_animation
from common import get_environment_path, get_viewport_camera_location, get_viewport_camera_rotation
from preview.common import SCENERY_FILENAME, MODEL_FILENAME


class EU07_OT_GameEnginePreviewScenery(bpy.types.Operator):
    bl_idname = "eu07.scenery_preview"
    bl_label = "Preview model in MaSzyna"

    def execute(self, context):
        settings = bpy.context.scene.eu07_scenery_preview

        root = get_environment_path()

        scenery_outpath = str(pathlib.Path(root, "scenery", SCENERY_FILENAME))
        bpy.ops.export_scene.scn(filepath=scenery_outpath)

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


        cwd = os.getcwd()
        os.chdir(root)

        args = [*settings.executable_command.split(" "), "-s", SCENERY_FILENAME]

        subprocess.Popen(args)

        os.chdir(cwd)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(EU07_OT_GameEnginePreviewScenery)


def unregister():
    bpy.utils.unregister_class(EU07_OT_GameEnginePreviewScenery)