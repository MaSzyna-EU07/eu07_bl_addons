import os
import pathlib

import bpy

import eu07_tools
from animation_tools.output.eventize import eventize_object_animation
from common import get_environment_path
from preview.common import SCENERY_FILENAME, MODEL_FILENAME, SUBDIR_NAME, transfer_external_textures, \
    create_camera_from_viewport, run_preview_command


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

        model_outpath = str(pathlib.Path(model_subdir, MODEL_FILENAME))
        bpy.ops.export_scene.t3d(
            filepath=model_outpath,
            aggregate_includes=True,
            embed_skins=True,
            objects_range='VISIBLE',
            path_mode='FILENAME',
            #use_generated_img_name=True
        )

        bpy.context.scene.frame_current = original_frame

        transfer_external_textures(tex_subdir)

        scn_elements = []

        node_model = create_node_model(settings.lights, settings.transition, settings.angles)
        scn_elements.append(node_model)

        camera = create_camera_from_viewport()
        scn_elements.append(camera)

        anim_elements = create_animation_elements()
        scn_elements.extend(anim_elements)

        if settings.use_track:
            track = create_track()
            scn_elements.append(track)

        if settings.use_ground:
            ground_level = -0.38 if settings.use_track else 0
            ground = create_ground_plane(ground_level)
            scn_elements.append(ground)

        scn_path = pathlib.Path(scenery_subdir, SCENERY_FILENAME)
        with open(scn_path, "w", encoding="windows-1250", newline="\r\n") as outfile:
            outfile.write("//$a\n")
            eu07_tools.scn.dump(scn_elements, outfile)

        run_preview_command(root, settings.executable_command)

        return {'FINISHED'}


def create_ground_plane(level):
    plane = eu07_tools.scn.create_element("node:triangles")
    plane.map = "grass"

    vertices = [
        [75, level, 75, 0, 1, 0, 10.4197, -9.4197],
        [-75, level, -75, 0, 1, 0, -9.4197, 10.4197],
        [-75, level, 75, 0, 1, 0, -9.4197, -9.4197],
        [75, level, 75, 0, 1, 0, 10.4197, -9.4197],
        [75, level, -75, 0, 1, 0, 10.4197, 10.4197],
        [-75, level, -75, 0, 1, 0, -9.4197, 10.4197],
    ]

    for vertex in vertices:
        plane.vertices.new(vertex)

    return plane


def create_node_model(lights, transition, angles):
    node_model = eu07_tools.scn.create_element("node:model")
    node_model.name = "model_preview"
    node_model.path = str(pathlib.Path(SUBDIR_NAME, MODEL_FILENAME))

    if lights:
        node_model.light_states = [float(state) for state in lights.strip(" ").split(" ")]
    # TODO: Light colors
    node_model.notransition = (not transition)
    node_model.rotation = eu07_tools.utils.swizzle_coords(angles)

    return node_model


def create_animation_elements():
    elements = []

    launcher = eu07_tools.scn.create_element("node:eventlauncher")
    launcher.key = "A"
    launcher.first_event_name = "animator"

    multiple = eu07_tools.scn.create_element("event:multiple")
    multiple.name = "animator"

    elements.extend([launcher, multiple])

    for obj in bpy.context.visible_objects:
        anim_events = eventize_object_animation(obj, "model_preview")
        multiple.events_names.extend(ev.name for ev in anim_events)
        elements.extend(anim_events)

    return elements


def create_track():
    track = eu07_tools.scn.create_element("node:track")
    track.p1 = (0, -0.18, -75)
    track.p2 = (0, -0.18, 75)
    track.map1 = "rail_screw_used1"
    track.map2 = "1435mm/tpd-stone3-new"
    track.geometry_params = [0.2, 0.5, 1.1]

    return track


def register():
    bpy.utils.register_class(EU07_OT_GameEnginePreviewModel)


def unregister():
    bpy.utils.unregister_class(EU07_OT_GameEnginePreviewModel)