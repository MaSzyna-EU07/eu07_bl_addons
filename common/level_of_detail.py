import bpy
from bpy_extras import view3d_utils


class EU07_OT_LevelOfDetailPreview(bpy.types.Operator):
    bl_idname = "eu07.level_of_detail_preview"
    bl_label = "LOD Preview"

    def invoke(self, context, event):
        self.hidden_objects = set()
        self._prev_active = None
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        viewport_position = bpy.context.space_data.region_3d.perspective_matrix.translation

        header_text = "LOD Preview: "

        for obj in bpy.context.scene.objects:
            distance_view_to_obj = abs((obj.location - viewport_position).magnitude)

            min_distance = obj.t3d_properties.min_distance
            max_distance = obj.t3d_properties.max_distance

            if bpy.context.active_object is obj or self._prev_active is obj:
                header_text += f"Distance to Active ({obj.name}): {round(distance_view_to_obj, 1)}m"
                header_text += f" | Visibility range: <{min_distance}; {max_distance}>"

            if max_distance == -1:
                max_distance = 99999

            hide = (
                    not (min_distance < distance_view_to_obj < max_distance)
            )

            if hide:
                if obj is bpy.context.active_object and not obj.hide_viewport:
                    self._prev_active = obj
                obj.hide_viewport = True
                self.hidden_objects.add(obj)
            else:
                if obj is self._prev_active and obj.hide_viewport:
                    obj.hide_viewport = False
                    obj.select_set(True)
                    bpy.context.view_layer.objects.active = self._prev_active
                    self._prev_active = None
                obj.hide_viewport = False

            if obj.parent and obj.parent.hide_viewport:
                obj.hide_viewport = True

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




