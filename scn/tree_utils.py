import bpy
import bmesh
import eu07_tools


inc_names = [
    "ljtree.inc",
    "ljtreebig.inc",
    "ljtreesmall.inc",
    "tree.inc",
    "treebig.inc",
    "treesmall.inc"
]


def instantiate_tree():
    tree_instance = bpy.data.objects.new("Tree", get_tree_template().data)
    tree_instance.material_slots[0].link = 'OBJECT'
    tree_instance.scn_properties.type_ = "tree"

    return tree_instance


def get_tree_template():
    tree_template = bpy.data.objects.get("TreeTemplate")

    if not tree_template:
        tree_template = bpy.data.objects.new("TreeTemplate", bpy.data.meshes.new("TreeTemplate"))
        tree_template.data.materials.append(None)
        tree_template.material_slots[0].link = 'OBJECT'


        mesh = bmesh.new()
        uv_layer = mesh.loops.layers.uv.new()

        geometry_data = [
            (1, 1, 0, 0, 0.99),
            (1, 0, 0, 0, 0),
            (-1, 1, 0, 1, 0.99),
            (-1, 0, 0, 1, 0),
            (-1, 1, 0, 1, 0.99),
            (1, 0, 0, 0, 0),
            (1, 0, 0, 0, 0),
            (1, 1, 0, 0, 0.99),
            (-1, 1, 0, 1, 0.99),
            (-1, 1, 0, 1, 0.99),
            (-1, 0, 0, 1, 0),
            (1, 0, 0, 0, 0),
            (0, 0, -1, 0, 0),
            (0, 1, -1, 0, 0.99),
            (0, 1, 1, 1, 0.99),
            (0, 1, 1, 1, 0.99),
            (0, 0, 1, 1, 0),
            (0, 0, -1, 0, 0),
            (0, 1, -1, 0, 0.99),
            (0, 0, -1, 0, 0),
            (0, 1, 1, 1, 0.99),
            (0, 0, 1, 1, 0),
            (0, 1, 1, 1, 0.99),
            (0, 0, -1, 0, 0)
        ]


        for i in range(len(geometry_data) // 3):
            vertex_index_start = i * 3
            vertex_index_end = vertex_index_start + 3

            face_verts_data = geometry_data[vertex_index_start:vertex_index_end]

            face_verts_coords = [eu07_tools.utils.swizzle_coords(vertex_data[:3]) for vertex_data in face_verts_data]

            face_verts = [mesh.verts.new(coords) for coords in face_verts_coords]
            face = mesh.faces.new(face_verts)

            for vertex_index, loop in enumerate(face.loops):
                loop[uv_layer].uv = face_verts_data[vertex_index][3:]

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


def get_tree_size(tree_instance):
    return (tree_instance.scale.z, tree_instance.scale.y)


def set_tree_material(tree_instance, material):
    tree_instance.material_slots[0].material = material
