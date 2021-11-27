import bpy
from bpy_extras import view3d_utils


class EU07_OT_LevelOfDetailPreview(bpy.types.Operator):
    bl_idname = "eu07.level_of_detail_preview"
    bl_label = "LOD Preview"

    def invoke(self, context, event):
        self.hidden_objects = set()
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        viewport_position = view3d_utils.region_2d_to_origin_3d(
            context.region, context.space_data.region_3d, (0.5, 0.5)
        )

        header_text = "LOD Preview: "

        for obj in bpy.context.scene.objects:
            distance_view_to_obj = abs((obj.location - viewport_position).magnitude)

            if bpy.context.active_object is obj:
                header_text += f"Distance to Active: {distance_view_to_obj}"

            min_distance = obj.t3d_properties.min_distance
            max_distance = obj.t3d_properties.max_distance

            if max_distance == -1:
                max_distance = 99999

            obj.hide_viewport = (
                    not (min_distance < distance_view_to_obj < max_distance)
            )

            if obj.hide_viewport:
                self.hidden_objects.add(obj)

        bpy.context.area.header_text_set(header_text)

        is_viewport_navigation_event = (
            "WHEEL" in event.type or
            "MOUSE" in event.type
        )

        if event.type == 'ESC':
            bpy.context.area.header_text_set("")

            for obj in self.hidden_objects:
                obj.hide_viewport = False

            return {'FINISHED'}
        elif is_viewport_navigation_event:
            return {'PASS_THROUGH'}
        else:
            return {'RUNNING_MODAL'}


classes = (
    EU07_OT_LevelOfDetailPreview,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)




