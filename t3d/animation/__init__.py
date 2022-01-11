import bpy

import mathutils

import eu07_tools

def eventize_object_animation(object, model_name):
    if not object.animation_data:
        return []

    action = object.animation_data.action

    fps = bpy.context.scene.render.fps
    frame_start, frame_end = action.frame_range

    # TODO: What if frame start is negative?
    total_duration = fps * (frame_end - frame_start)

    keyframes = {
        "rotation": {},
        "location": {}
    }

    for fc in action.fcurves:
        for keyframe in fc.keyframe_points:
            keyframe, value = keyframe.co

            start_time = keyframe / fps

            vector = mathutils.Vector((0, 0, 0))
            vector[fc.array_index] = value

            keyframes[fc.data_path][start_time] = vector

    events = []

    for data_path, subdict in keyframes.items():
        prev_start_time = 0
        prev_vector = mathutils.Vector((0, 0, 0))

        i = 0
        for start_time, vector in subdict.items():
            duration = start_time - prev_start_time
            vector = vector - prev_vector

            if duration == 0 or vector.magnitude == 0:
                continue

            event = eu07_tools.scn.create_element("event:animation")
            event.delay = start_time
            event.name = f"{model_name}_anim_{data_path}_{i}"
            event.anim_type = "translate" if data_path == "location" else "rotate"
            event.model_name = model_name
            event.submodel_name = object.name
            event.speed = vector.magnitude / duration
            event.vector = vector

            i += 1

            events.append(event)

    # TODO: Merge events with same speed, type and delay

    return events
