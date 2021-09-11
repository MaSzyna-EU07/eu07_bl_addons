import math
from pathlib import Path

import bmesh
import eu07_tools

from scn import tree_utils
from common import get_root, get_path_from_material
from .. import trajectory_tools



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
        node.map = get_path_from_material(material)

        for local_vert_idx, global_vert_idx in enumerate(polygon.vertices):
            vertex = mesh.vertices[global_vert_idx]

            xyz = eu07_tools.utils.swizzle_coords(vertex.co)
            ijk = eu07_tools.utils.swizzle_coords(vertex.normal)

            if uv_layer:
                mesh_loop_idx = polygon.loop_indices[local_vert_idx]
                uv = uv_layer.data[mesh_loop_idx].uv
            else:
                uv = [0, 0]

            node.vertices.new((*xyz, *ijk, *uv))
        yield node


def create_tree_include(tree_object):
    tree_inc = eu07_tools.scn.create_element("include")
    tree_inc.path = "tree.inc"
    tree_inc.parameters.append(get_path_from_material(tree_object.active_material))
    tree_inc.parameters.extend(eu07_tools.utils.swizzle_coords(tree_object.location))
    tree_inc.parameters.append(math.degrees(tree_object.rotation_euler[2]))
    tree_inc.parameters.extend(tree_utils.get_tree_size(tree_object))

    tree_inc.parameters = [str(p) for p in tree_inc.parameters]

    return tree_inc


def create_node_track(track_object):
    properties = track_object.scn_properties

    mesh = next(c for c in track_object.children if c.name.startswith("TrajectoryProfileTemplate"))

    node = eu07_tools.scn.create_element("node:track")
    node.subtype = properties.type_.split(":")[-1]
    node.name = track_object.name
    node.max_distance = properties.node_max_distance
    node.min_distance = properties.node_min_distance
    node.length = spline = track_object.data.splines[0].calc_length()
    node.width = properties.trajectory_width 
    node.friction = properties.trajectory_friction
    node.sound_distance = properties.trajectory_sound_distance
    node.quality_flag = properties.trajectory_quality
    node.damage_flag = properties.trajectory_damage
    node.environment = properties.trajectory_environment
    node.is_visible = properties.trajectory_visible
    node.map1 = get_path_from_material(mesh.material_slots[0].material)
    node.map2 = get_path_from_material(mesh.material_slots[1].material)
    node.mapping_length = properties.trajectory_mapping_length
    node.event0 = properties.trajectory_event0
    node.event1 = properties.trajectory_event1
    node.event2 = properties.trajectory_event2
    node.eventall0 = properties.trajectory_eventall0
    node.eventall1 = properties.trajectory_eventall1
    node.eventall2 = properties.trajectory_eventall2
    node.isolated = properties.trajectory_isolated
    node.overhead = properties.trajectory_overhead
    node.angle1 = properties.trajectory_angle1
    node.angle2 = properties.trajectory_angle2
    node.fouling1 = properties.trajectory_fouling1
    node.fouling2 = properties.trajectory_fouling2
    node.vradius = properties.trajectory_vradius
    node.railprofile = properties.trajectory_railprofile
    node.friction_memcell_name = properties.trajectory_friction_memcell_name

    profile_instance = trajectory_tools.get_profile_instance(track_object)

    curve_data = extract_curve_data_for_scn(track_object)
    node.p1 = curve_data[0]
    node.cv1 = curve_data[1]
    node.cv2 = curve_data[2]
    node.p2 = curve_data[3]

    if (node.is_junction):
        junction_track_object = next((c for c in track_object.children if c.type == 'CURVE'))

        junction_mesh = next(c for c in track_object.children if c.name.startswith("TrajectoryProfileTemplate"))

        curve_data = extract_curve_data_for_scn(junction_track_object)
        node.p3 = curve_data[0]
        node.cv3 = curve_data[1]
        node.cv4 = curve_data[2]
        node.p4 = curve_data[3]

        node.map1 = get_path_from_material(mesh.material_slots[0].material)
        node.map2 = get_path_from_material(junction_mesh.material_slots[0].material)

        node.trackbed = get_path_from_material(mesh.material_slots[1].material)
    else:
        node.geometry_params = trajectory_tools.get_profile_params(profile_instance)


    return node

def extract_curve_data_for_scn(track_object):
    spline = track_object.data.splines[0]

    values = []

    p1 = eu07_tools.utils.swizzle_coords(track_object.matrix_world.translation + spline.bezier_points[0].co)

    p2 = eu07_tools.utils.swizzle_coords(track_object.matrix_world.translation + spline.bezier_points[1].co)

    # AUTO type because curve modifier works bad when we set both handles at the same position as vertex, so little cheat there
    cv1 = spline.bezier_points[0].handle_right if spline.bezier_points[0].handle_right_type != 'AUTO' else (0, 0, 0)
    cv2 = spline.bezier_points[1].handle_left if spline.bezier_points[1].handle_left_type != 'AUTO' else (0, 0, 0)

    cv1 = eu07_tools.utils.swizzle_coords(cv1)
    if spline.bezier_points[1].handle_left_type != 'AUTO':
        cv2 = eu07_tools.utils.swizzle_coords(cv2 - spline.bezier_points[1].co)

    return [p1, cv1, cv2, p2]
    

