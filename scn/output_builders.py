from pathlib import Path

import bmesh
import bpy
import eu07_tools
from eu07_bl_addons.common import get_root

def create_node_triangles_from_mesh(mesh):
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    uv_layer = mesh.uv_layers.active

    mesh.validate_material_indices()
    for polygon in mesh.polygons:
        node = eu07_tools.scn.create_element("node:triangles")

        material = mesh.materials[polygon.material_index]
        if material:
            tex_node = material.node_tree.nodes.get("texture_diffuse")
            if tex_node:
                img_path = tex_node.image.filepath
                node.map = eu07_tools.utils.shorten_asset_path(
                    bpy.path.abspath(img_path)
                )

        for local_vert_idx, global_vert_idx in enumerate(polygon.vertices):
            vertex = mesh.vertices[global_vert_idx]

            xyz = eu07_tools.utils.switch_coordinate_system(vertex.co)
            ijk = eu07_tools.utils.switch_coordinate_system(vertex.normal)

            if uv_layer:
                mesh_loop_idx = polygon.loop_indices[local_vert_idx]
                uv = uv_layer.data[mesh_loop_idx].uv
            else:
                uv = [0, 0]

            node.vertices.new((*xyz, *ijk, *uv))
        yield node