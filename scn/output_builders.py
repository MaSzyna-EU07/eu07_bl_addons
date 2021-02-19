from pathlib import Path

import bmesh
import bpy
import eu07_tools
from ..common import get_root


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

def create_node_track(track_object):
    properties = track_object.scn_properties

    node = eu07_tools.scn.create_element("node:track")
    node.subtype = properties.type_.split(":")[-1]
    node.name = track_object.name
    node.max_distance = properties.node_max_distance
    node.min_distance = properties.node_min_distance
    node.width = properties.trajectory_width
    node.friction = properties.trajectory_friction
    node.sound_distance = properties.trajectory_sound_distance
    node.quality_flag = properties.trajectory_quality
    node.damage_flag = properties.trajectory_damage
    node.environment = properties.trajectory_environment
    node.is_visible = properties.trajectory_visible
    node.mapping_length = properties.trajectory_mapping_length

    return node

def get_material_paths(obj):
    paths = []

    for ms in obj.material_slots:
        if (ms.material is None):
            paths.append("none")
        else:
            paths.append(ms.material.name)

    return paths

