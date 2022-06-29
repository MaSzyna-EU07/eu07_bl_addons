import math
import os
import pathlib
import subprocess
import shutil

import bpy

import eu07_tools
from animation_tools.output.eventize import eventize_object_animation
from common import get_environment_path, get_viewport_camera_location, get_viewport_camera_rotation
from preview.common import SCENERY_FILENAME, MODEL_FILENAME, SUBDIR_NAME

from material_tools.utils import MaterialWrapper


# TODO: Split this to shorter functions
class EU07_OT_GameEnginePreviewModel(bpy.types.Operator):
    bl_idname = "eu07.model_preview"
    bl_label = "Preview model in MaSzyna"

    def execute(self, context):
        settings = bpy.context.scene.eu07_model_preview

        root = get_environment_path()

        scenery_subdir = pathlib.Path(root, "scenery", SUBDIR_NAME)
        model_subdir = pathlib.Path(root, "models", SUBDIR_NAME)
        tex_subdir = pathlib.Path(root, "textures", SUBDIR_NAME)

        os.makedirs(scenery_subdir, exist_ok=True)
        os.makedirs(model_subdir, exist_ok=True)

        original_frame = bpy.context.scene.frame_current
        bpy.context.scene.frame_current = bpy.context.scene.frame_start

        model_outpath = str(pathlib.Path(root, "models", SUBDIR_NAME, MODEL_FILENAME))
        bpy.ops.export_scene.t3d(
            filepath=model_outpath,
            aggregate_includes=True,
            embed_skins=True,
            objects_range='VISIBLE',
            path_mode='FILENAME',
            #use_generated_img_name=True
        )

# ----------------------------------------------------

        shutil.rmtree(tex_subdir, ignore_errors=True)
        os.makedirs(tex_subdir, exist_ok=True)

        for obj in bpy.context.visible_objects:
            if not obj.active_material:
                break

            #TODO: .mat support

            wrapper = MaterialWrapper(obj.active_material)
            diffuse = wrapper.get_diffusemap()

            if not diffuse:
                break

            diffuse_filepath = pathlib.Path(bpy.path.abspath(diffuse.filepath))
            dst = pathlib.Path(tex_subdir, diffuse_filepath.name)


            if diffuse.packed_file:
                data = diffuse.packed_file.data
                with open(dst, "wb+") as outimage:
                    outimage.write(data)
            elif diffuse.source == 'GENERATED':
                name = diffuse.name.replace(".", "_")
                # TODO: Make it happen xD
                #
                # newimg = bpy.data.images.new(
                #     f"{name}_forpreview",
                #     width=diffuse.generated_width,
                #     height=diffuse.generated_height
                # )
                #
                # newimg.pixels = diffuse.pixels
                # newimg.filepath_raw = str(dst / f"{name}.tga")
                # newimg.file_format = 'TARGA'
                # newimg.save()
                #
                # bpy.data.images.remove(newimg)

            else:
                try:
                    dst.symlink_to(diffuse_filepath)
                except FileExistsError:
                    pass


        bpy.context.scene.frame_current = original_frame

        scn_elements = []

        node_model = eu07_tools.scn.create_element("node:model")
        node_model.name = "model_preview"
        node_model.path = str(pathlib.Path(SUBDIR_NAME, MODEL_FILENAME))

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

        for obj in bpy.context.visible_objects:
            anim_events = eventize_object_animation(obj, "model_preview")
            multiple.events_names.extend(ev.name for ev in anim_events)
            scn_elements.extend(anim_events)


        if settings.use_track:
            track = eu07_tools.scn.create_element("node:track")
            track.p1 = (0, -0.18, -75)
            track.p2 = (0, -0.18, 75)
            track.map1 = "rail_screw_used1"
            track.map2 = "1435mm/tpd-stone3-new"
            track.geometry_params = [0.2, 0.5, 1.1]

            scn_elements.append(track)

        scn_path = pathlib.Path(root, "scenery", SUBDIR_NAME, SCENERY_FILENAME)
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

        args = [*settings.executable_command.split(" "), "-s", pathlib.Path(SUBDIR_NAME, SCENERY_FILENAME)]

        subprocess.Popen(args)

        os.chdir(cwd)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(EU07_OT_GameEnginePreviewModel)


def unregister():
    bpy.utils.unregister_class(EU07_OT_GameEnginePreviewModel)