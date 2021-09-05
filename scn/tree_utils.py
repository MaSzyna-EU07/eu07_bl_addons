import bpy
import bmesh


def instantiate_tree():
    tree_instance = bpy.data.objects.new("Tree", get_tree_template().data)
    tree_instance.material_slots[0].link = 'OBJECT'

    return tree_instance


def get_tree_template():
    tree_template = bpy.data.objects.get("TreeTemplate")

    if not tree_template:
        tree_template = bpy.data.objects.new("TreeTemplate", bpy.data.meshes.new("TreeTemplate"))
        tree_template.data.materials.append(None)
        tree_template.material_slots[0].link = 'OBJECT'

        mesh = bmesh.new()
        uv_layer = mesh.loops.layers.uv.new()

        verts = [
            mesh.verts.new((-0.5, 0, 0)),
            mesh.verts.new((0.5, 0, 0)),
            mesh.verts.new((0.5, 0, 1)),
            mesh.verts.new((-0.5, 0, 1)),

            mesh.verts.new((-0.5, 0, 0)),
            mesh.verts.new((0.5, 0, 0)),
            mesh.verts.new((0.5, 0, 1)),
            mesh.verts.new((-0.5, 0, 1)),

            mesh.verts.new((0, -0.5, 0)),
            mesh.verts.new((0, 0.5, 0)),
            mesh.verts.new((0, 0.5, 1)),
            mesh.verts.new((0, -0.5, 1)),

            mesh.verts.new((0, -0.5, 0)),
            mesh.verts.new((0, 0.5, 0)),
            mesh.verts.new((0, 0.5, 1)),
            mesh.verts.new((0, -0.5, 1)),
        ]

        uvs = [
            (0, 0),
            (1, 0),
            (1, 1),
            (0, 1)
        ]

        for i in range(4):
            face = mesh.faces.new(verts[i * 4:i * 4 + 4])

            for vertex_index, loop in enumerate(face.loops):
                loop[uv_layer].uv = uvs[vertex_index]

            if i % 2 == 0:
                face.normal_flip()

        mesh.to_mesh(tree_template.data)
        mesh.free()

        collection = bpy.data.collections.get("Templates") or bpy.data.collections.new("Templates")
        collection.objects.link(tree_template)

    return tree_template


def set_tree_size(tree_instance, height, breadth):
    tree_instance.scale.x = breadth
    tree_instance.scale.y = breadth
    tree_instance.scale.z = height


def set_tree_material(tree_instance, material):
    tree_instance.material_slots[0].material = material
