import math

import bpy

import mathutils

import eu07_tools


class KeyframeData:
    def __init__(self, animated_property, delay, time_to_next, vector):
        self.animated_property = animated_property
        self.delay = delay
        self.time_to_next = time_to_next
        self.vector = vector


class KeyframeDataStorage:
    def __init__(self):
        self._groups = {
            "location": {},
            "rotation_euler": {}
        }

    def iter_groups(self):
        return iter(d.values() for d in self._groups.values())

    def fill_from_action(self, action):
        fps = bpy.context.scene.render.fps

        frames_range = range(bpy.context.scene.frame_start, bpy.context.scene.frame_end + 1)

        for fcurve in action.fcurves:
            delays = [kf.co[0] / fps for kf in fcurve.keyframe_points]

            for kf_idx, kf in enumerate(fcurve.keyframe_points):
                if kf.co[0] not in frames_range:
                    continue

                delay = delays[kf_idx]
                try:
                    next_delay = delays[kf_idx + 1]
                except IndexError:
                    time_to_next = 0
                else:
                    time_to_next = next_delay - delay

                vector = mathutils.Vector()
                vector[fcurve.array_index] = kf.co[1]

                kf_data = KeyframeData(fcurve.data_path, delay, time_to_next, vector)
                self._store(kf_data)

    def _store(self, kf_data):
        key = (kf_data.delay, kf_data.time_to_next)
        group = self._groups[kf_data.animated_property]

        if key in group:
            group[key].vector += kf_data.vector
        else:
            group[key] = kf_data


def eventize_object_animation(object, model_name, name_prefix=""):
    # Works only when:
    # There are no keyframes outside action.frame_range
    # And range is in <0;inf)
    # TODO: Fix those issues

    if not object.animation_data:
        return []
    elif not object.animation_data.action:
        return []

    keyframes_storage = KeyframeDataStorage()
    keyframes_storage.fill_from_action(object.animation_data.action)

    events = []

    for keyframe_group in keyframes_storage.iter_groups():

        keyframe_group = list(keyframe_group)

        keyframe_group = sorted(keyframe_group, key=(lambda x: x.delay))

        prev_data = None

        for kf_index, kf_data in enumerate(keyframe_group):

            if prev_data is None:
                prev_data = kf_data
                continue

            if kf_data.animated_property == "rotation_euler":
                kf_data.vector = mathutils.Vector([math.degrees(x) for x in kf_data.vector])

            event = eu07_tools.scn.create_element("event:animation")
            event.delay = prev_data.delay
            event.anim_type = "translate" if kf_data.animated_property == "location" else "rotate"
            prefix_sep = "_" if name_prefix else ""
            event.name = f"{name_prefix}{prefix_sep}{object.animation_data.action.name}_{event.anim_type}{kf_index}"
            event.model_name = model_name
            event.submodel_name = object.name
            event.speed = kf_data.vector.magnitude / prev_data.time_to_next
            event.vector = kf_data.vector

            prev_data = kf_data

            events.append(event)

    return events
