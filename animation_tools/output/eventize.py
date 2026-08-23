import math

import bpy

import mathutils
from bpy_extras import anim_utils

import eu07_tools


def iter_fcurves(anim_data):
    """Blender 5.0 removed ``Action.fcurves``/``Action.groups``.

    F-curves now live in the channelbag of the action slot that is assigned
    to the animated ID, so they have to be looked up through the anim data.
    """
    if anim_data is None:
        return ()

    channelbag = anim_utils.animdata_get_channelbag_for_assigned_slot(anim_data)
    if channelbag is None:
        return ()

    return channelbag.fcurves


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

    def fill_from_anim_data(self, anim_data):
        fps = bpy.context.scene.render.fps

        frame_start = bpy.context.scene.frame_start
        frame_end = bpy.context.scene.frame_end
        frames_range = range(frame_start, frame_end + 1)


        for fcurve in iter_fcurves(anim_data):
            if fcurve.data_path not in self._groups:
                continue

            delays = [(kf.co[0] - frame_start) / fps for kf in fcurve.keyframe_points]

            print(delays)

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

                if fcurve.data_path == "rotation_euler":
                    vector = mathutils.Vector([math.degrees(x) for x in vector])

                kf_data = KeyframeData(fcurve.data_path, delay, time_to_next, vector)
                self._store(kf_data)

    def _store(self, kf_data):
        key = (kf_data.delay, kf_data.time_to_next)
        group = self._groups[kf_data.animated_property]

        if key in group:
            group[key].vector += kf_data.vector
        else:
            group[key] = kf_data


def eventize_object_animation(obj, model_name, name_prefix=""):
    # Works only when:
    # There are no keyframes outside action.frame_range
    # TODO: Fix those issues

    if not obj.animation_data:
        return []
    elif not obj.animation_data.action:
        return []

    keyframes_storage = KeyframeDataStorage()
    keyframes_storage.fill_from_anim_data(obj.animation_data)

    events = []

    for keyframe_group in keyframes_storage.iter_groups():

        keyframe_group = list(keyframe_group)

        keyframe_group = sorted(keyframe_group, key=(lambda x: x.delay))

        prev_data = None

        for kf_index, kf_data in enumerate(keyframe_group):

            if prev_data is None:
                prev_data = kf_data
                continue

            # frame reduction
            if prev_data.vector == kf_data.vector:
                prev_data = kf_data
                continue

            event = eu07_tools.scn.create_element("event:animation")
            event.delay = prev_data.delay
            event.anim_type = "translate" if kf_data.animated_property == "location" else "rotate"
            prefix_sep = "_" if name_prefix else ""
            event.name = f"{name_prefix}{prefix_sep}{obj.animation_data.action.name}_{event.anim_type}{kf_index}"
            event.model_name = model_name
            event.submodel_name = obj.name
            event.speed = (kf_data.vector - prev_data.vector).magnitude / prev_data.time_to_next

            event.speed *= -1 if event.anim_type == "rotate" else 1

            event.vector = kf_data.vector - obj.location

            prev_data = kf_data

            events.append(event)

    return events
