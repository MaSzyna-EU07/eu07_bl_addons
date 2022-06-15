import math
import os
import pathlib
import subprocess

import bpy

import eu07_tools
from animation_tools.output.eventize import eventize_object_animation
from common import get_environment_path, get_viewport_camera_location, get_viewport_camera_rotation
from preview.common import SCENERY_FILENAME, MODEL_FILENAME


class EU07_OT_GameEnginePreviewModel(bpy.types.Operator):
    bl_idname = "eu07.model_preview"
    bl_label = "Preview model in MaSzyna"

    def execute(self, context):
        settings = bpy.context.scene.eu07_model_preview

        root = get_environment_path()

        original_frame = bpy.context.scene.frame_current
        bpy.context.scene.frame_current = bpy.context.scene.frame_start

        model_outpath = str(pathlib.Path(root, "models", MODEL_FILENAME))
        bpy.ops.export_scene.t3d(filepath=model_outpath, aggregate_includes=True, embed_skins=True, objects_range='VISIBLE')

        bpy.context.scene.frame_current = original_frame

        scn_elements = []

        node_model = eu07_tools.scn.create_element("node:model")
        node_model.name = "model_preview"
        node_model.path = MODEL_FILENAME

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


        launcher = eu07_tools.scn.create_element("node:eventlauncher")
        launcher.key = "A"
        launcher.first_event_name = "animator"

        multiple = eu07_tools.scn.create_element("event:multiple")
        multiple.name = "animator"

        scn_elements.extend([launcher, multiple])

        for obj in bpy.data.objects:
            anim_events = eventize_object_animation(obj, "model_preview")
            multiple.events_names.extend(ev.name for ev in anim_events)
            scn_elements.extend(anim_events)


        if settings.use_track:
            track = eu07_tools.scn.create_element("node:track")
            track.p1 = (0, -0.18, -75)
            track.p2 = (0, -0.18, 75)
            track.map1 = "rail_screw_used1"
            track.map2 = "tpbps-new3"
            track.geometry_params = [0.2, 0.5, 1.1]

            scn_elements.append(track)

        scn_path = pathlib.Path(root, "scenery", SCENERY_FILENAME)
        with open(scn_path, "w", encoding="windows-1250", newline="\r\n") as outfile:
            outfile.write("//$a\n")
            if settings.use_ground:
                track_lower = -0.38 if settings.use_track else 0

                outfile.write(
                    "node -1 0 none triangles grass\n"
                    f"75 {track_lower} 75 0 1 0 10.4197 -9.4197 end\n"
                    f"-75 {track_lower} -75 0 1 0 -9.4197 10.4197 end\n"
                    f"-75 {track_lower} 75 0 1 0 -9.4197 -9.4197 end\n"
                    f"75 {track_lower} 75 0 1 0 10.4197 -9.4197 end\n"
                    f"75 {track_lower} -75 0 1 0 10.4197 10.4197 end\n"
                    f"-75 {track_lower} -75 0 1 0 -9.4197 10.4197\n"
                    "endtri\n"
                )
            eu07_tools.scn.dump(scn_elements, outfile)

        cwd = os.getcwd()
        os.chdir(root)

        args = [*settings.executable_command.split(" "), "-s", SCENERY_FILENAME]

        subprocess.Popen(args)

        os.chdir(cwd)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(EU07_OT_GameEnginePreviewModel)


def unregister():
    bpy.utils.unregister_class(EU07_OT_GameEnginePreviewModel)