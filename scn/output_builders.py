from pathlib import Path

import bmesh
import eu07_tools
from eu07_bl_addons.common import get_root

def create_node_triangles_from_mesh(mesh):
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    uv_layer = mesh.uv_layers.active

    for polygon in mesh.polygons:
        node = eu07_tools.scn.create_element("node:triangles")

        material = mesh.materials[polygon.material_index]
        tex_node = material.node_tree.nodes.get("texture_diffuse")
        if tex_node:
            img_path = tex_node.image.filepath
            node.map = str(
                Path(img_path)
                .relative_to(get_root(img_path))
                .with_suffix("")
            )

        for local_vert_idx, global_vert_idx in enumerate(polygon.vertices):
            vertex = mesh.vertices[global_vert_idx]

            xyz = vertex.co

            if uv_layer:
                mesh_loop_idx = polygon.loop_indices[local_vert_idx]
                uv = uv_layer.data[mesh_loop_idx].uv
            else:
                uv = [0, 0]

            node.vertices.new((*xyz, *uv))
        yield node