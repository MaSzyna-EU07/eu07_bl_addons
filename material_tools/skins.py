import bpy


class EU07_OT_BroadcastSkin(bpy.types.Operator):
    bl_idname = "eu07.broadcast_skin"
    bl_label = "Broadcast Skin"

    @classmethod
    def poll(cls, context):
        return (
            context.active_object.t3d_properties.replacableskin_id != "None" and
            context.active_object.active_material
        )

    def execute(self, context):
        replacableskin_id = context.active_object.t3d_properties.replacableskin_id

        for obj in bpy.data.objects:
            if obj.t3d_properties.replacableskin_id == replacableskin_id:
                obj.active_material = context.active_object.active_material

        return {'FINISHED'}


classes = (
    EU07_OT_BroadcastSkin,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)