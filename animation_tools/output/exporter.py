import bpy

import eu07_tools

from .eventize import eventize_object_animation


class AnimationExporter:
    def __init__(self):
        self.objects_range = "ALL"
        self.model_name = ""
        self.main_event_name = ""

    def export_to_filepath(self, filepath):
        with open(filepath, mode="w+", encoding="windows-1250", newline="\r\n") as out_file:
            self.export_to_file(out_file)

    def export_to_file(self, file):
        objects = bpy.context.scene.objects
        if self.objects_range == "SELECTION":
            objects = bpy.context.selected_objects
        elif self.objects_range == "VISIBLE":
            objects = bpy.context.visible_objects
        elif self.objects_range == "ACTIVE_COLLECTION":
            objects = bpy.context.collection

        elements = []

        if self.main_event_name != "":
            multiple = eu07_tools.scn.create_element("event:multiple")
            multiple.name = self.main_event_name

            elements.append(multiple)

        if self.model_name == "":
            self.model_name = "none"

        original_frame = bpy.context.scene.frame_current
        bpy.context.scene.frame_current = bpy.context.scene.frame_start

        for obj in objects:
            elements.extend(eventize_object_animation(obj, self.model_name))

        bpy.context.scene.frame_current = original_frame

        eu07_tools.scn.dump(elements, file)

