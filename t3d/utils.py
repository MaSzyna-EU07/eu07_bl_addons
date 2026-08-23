import bpy

def join_meshes_into_one(objects):
    if not objects:
        return None

    for obj in objects:
        bpy.context.scene.collection.objects.link(obj)

    target = objects[0]

    override = {
        "object": target,
        "active_object": target,
        "selected_objects": objects,
        "selected_editable_objects": objects,
    }

    meshes_to_remove = [o.data for o in objects if o is not target]

    with bpy.context.temp_override(**override):
        bpy.ops.object.transform_apply()
        bpy.ops.object.join()

    for m in meshes_to_remove:
        bpy.data.meshes.remove(m)

    bpy.context.scene.collection.objects.unlink(target)

    return target
