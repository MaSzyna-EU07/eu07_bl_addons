import bpy

from .structures import matblock as matblock_mod, randomtextureset as randomtextureset_mod

class EU07_OT_ProvideMATNodeGroups(bpy.types.Operator):
    bl_label = "Provide MAT Nodes"
    bl_idname = "eu07.provide_mat_nodes"

    def execute(self, context):
        matblock_mod.get_template()
        randomtextureset_mod.get_template()

        return {'FINISHED'}


classes = (
    EU07_OT_ProvideMATNodeGroups,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)