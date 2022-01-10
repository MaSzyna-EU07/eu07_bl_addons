import bpy
import collections

import eu07_tools

def eventize_object_animation(object, model_name):
    if not object.anim_data:
        return []

    action = object.anim_data.action

    fps = bpy.context.scene.render.fps
    frame_start, frame_end = object.anim_data.frame_range

    # TODO: What if frame start is negative?
    total_duration = fps * (frame_end - frame_start)

    keyframes = {
        "rotation": {},
        "location": {}
    }

    for fc in action.fcurves:
        for keyframe in fc.keyframe_points:
            keyframe, value = keyframe.co

            start_time = fps * keyframe

            vector = mathutils.Vector((0, 0, 0))
            vector[fc.array_index] = value

            keyframes[start_time] = vector

    events = []

    for data_path, subdict in keyframes:
        prev_start_time = 0
        prev_vector = mathutils.Vector((0, 0, 0))

        for start_time, vector in subdict.items():
            duration = start_time - prev_start_time
            vector = vector - prev_vector

            if duration == 0 or vector.magnitude == 0:
                continue

            event = eu07_tools.scn.create_element("event:animation")
            event.delay = start_time
            event.anim_type = "translate" if data_path == "location" else "rotate"
            event.model_name = model_name
            event.submodel_name = object.name
            event.speed = vector.magnitude / duration

            events.append(event)

    # TODO: Merge events with same speed, type and delay

    return events
