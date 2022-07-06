import copy
import os
import pathlib

import bpy

import eu07_tools
from animation_tools.output.eventize import eventize_object_animation
from common import get_environment_path
from preview.common import SCENERY_FILENAME, MODEL_FILENAME, SUBDIR_NAME, transfer_external_textures, \
    create_camera_from_viewport, run_preview_command, NODE_MODEL_NAME


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
    node_model.name = NODE_MODEL_NAME
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

    resetables = []

    for obj in bpy.context.visible_objects:
        anim_events = eventize_object_animation(obj, NODE_MODEL_NAME)

        if anim_events:
            multiple.events_names.extend(ev.name for ev in anim_events)
            elements.extend(anim_events)
            resetables.append(obj)

    reset_elements = create_reset_anim_elements(resetables)
    elements.extend(reset_elements)

    return elements


def create_reset_anim_elements(resetables):
    reset_launcher = eu07_tools.scn.create_element("node:eventlauncher")
    reset_launcher.key = "R"
    reset_launcher.first_event_name = "reset_anim"

    reset_multiple = eu07_tools.scn.create_element("event:multiple")
    reset_multiple.name = "reset_anim"

    elements = [
        reset_launcher, reset_multiple
    ]

    for obj in resetables:
        reset_rotate = eu07_tools.scn.create_element("event:animation")
        reset_rotate.name = f"{obj.name}_reset_rotate"
        reset_rotate.vector = 0, 0, 0
        reset_rotate.speed = 100
        reset_rotate.anim_type = "rotate"
        reset_rotate.model_name = NODE_MODEL_NAME
        reset_rotate.submodel_name = obj.name

        reset_translate = eu07_tools.scn.create_element("event:animation")
        reset_translate.name = f"{obj.name}_reset_translate"
        reset_translate.vector = 0, 0, 0
        reset_translate.speed = 100
        reset_translate.anim_type = "translate"
        reset_translate.model_name = NODE_MODEL_NAME
        reset_translate.submodel_name = obj.name

        elements.extend([reset_rotate, reset_translate])

        reset_multiple.events_names.extend([reset_rotate.name, reset_translate.name])

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