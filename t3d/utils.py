import bpy

def join_meshes_into_one(objects):
    if not objects:
        return None

    for obj in objects:
        bpy.context.scene.collection.objects.link(obj)

    c = {}
    c["object"] = c["active_object"] = objects[0]
    c["selected_objects"] = c["selected_editable_objects"] = objects

    meshes_to_remove = [o.data for o in c["selected_objects"] if o is not c["object"]]

    bpy.ops.object.transform_apply(c)
    bpy.ops.object.join(c)

    for m in meshes_to_remove:
        bpy.data.meshes.remove(m)

    bpy.context.scene.collection.objects.unlink(c["object"])

    return c["object"]