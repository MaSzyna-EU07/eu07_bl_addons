import math

import bpy

import eu07_tools
from material_tools.utils import get_shortpath_from_material

from scn.trajectory_tools.profile import get_params, get_instance


def create(name, location=None):
    curve = bpy.data.objects.new(name, bpy.data.curves.new(name, 'CURVE'))
    trajectory = setup_trajectory(curve)

    if location is not None:
        trajectory.location = location

    return trajectory


def setup_trajectory(curve):
    curve.data.dimensions = "3D"
    curve.data.use_stretch = True
    curve.data.use_deform_bounds = True

    spline = curve.data.splines.new('BEZIER')
    spline.use_smooth = False
    spline.bezier_points.add(1)


def create_element_from_track(track_object):
    properties = track_object.scn_properties

    if track_object.parent and "node:track" in track_object.parent.scn_properties.type_:
        return None

    mesh = next(c for c in track_object.children if c.name.startswith("TrajectoryProfileTemplate"))

    node = eu07_tools.scn.create_element("node:track")
    node.subtype = properties.type_.split(":")[-1]
    node.name = track_object.name
    node.max_distance = properties.node_max_distance
    node.min_distance = properties.node_min_distance
    node.length = track_object.data.splines[0].calc_length()
    node.width = properties.trajectory_width
    node.friction = properties.trajectory_friction
    node.sound_distance = properties.trajectory_sound_distance
    node.quality_flag = properties.trajectory_quality
    node.damage_flag = properties.trajectory_damage
    node.environment = properties.trajectory_environment
    node.is_visible = properties.trajectory_visible
    node.map1 = get_shortpath_from_material(mesh.material_slots[0].material)
    node.map2 = get_shortpath_from_material(mesh.material_slots[1].material)
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

    profile_instance = get_instance(track_object)

    curve_data = extract_curve_data_for_scn(track_object)
    node.p1 = curve_data[0]
    node.cv1 = curve_data[1]
    node.cv2 = curve_data[2]
    node.p2 = curve_data[3]
    node.p1_roll = math.degrees(track_object.data.splines[0].bezier_points[0].tilt)
    node.p2_roll = math.degrees(track_object.data.splines[0].bezier_points[1].tilt)

    if (node.is_junction):

        junction_track_object = next((c for c in track_object.children if c.type == 'CURVE'))

        junction_mesh = next(c for c in track_object.children if c.name.startswith("TrajectoryProfileTemplate"))

        curve_data = extract_curve_data_for_scn(junction_track_object)
        node.p3 = curve_data[0]
        node.cv3 = curve_data[1]
        node.cv4 = curve_data[2]
        node.p4 = curve_data[3]
        node.p3_roll = math.degrees(junction_track_object.data.splines[0].bezier_points[0].tilt)
        node.p4_roll = math.degrees(junction_track_object.data.splines[0].bezier_points[1].tilt)

        node.map1 = get_shortpath_from_material(mesh.material_slots[0].material)
        node.map2 = get_shortpath_from_material(junction_mesh.material_slots[0].material)

        node.trackbed = get_shortpath_from_material(mesh.material_slots[1].material)
    else:
        node.geometry_params = get_params(profile_instance)


    return node


def extract_curve_data_for_scn(track_object):
    spline = track_object.data.splines[0]

    is_straight = is_track_straight(track_object)

    p1 = eu07_tools.utils.swizzle_coords(track_object.matrix_world.translation + spline.bezier_points[0].co)

    p2 = eu07_tools.utils.swizzle_coords(track_object.matrix_world.translation + spline.bezier_points[1].co)

    cv1 = (0, 0, 0) if is_straight else spline.bezier_points[0].handle_right
    cv2 = (0, 0, 0) if is_straight else spline.bezier_points[1].handle_left

    if not is_straight:
        cv1 = eu07_tools.utils.swizzle_coords(cv1 - spline.bezier_points[0].co)
        cv2 = eu07_tools.utils.swizzle_coords(cv2 - spline.bezier_points[1].co)

    return [p1, cv1, cv2, p2]


def is_track_straight(track_object):
    spline = track_object.data.splines[0]

    p1 = spline.bezier_points[0].co
    cv1 = spline.bezier_points[0].handle_right
    cv2 = spline.bezier_points[1].handle_left

    ab = (p1 + cv1).magnitude
    ac = (p1 + cv2).magnitude
    bc = (cv1 + cv2).magnitude

    return ab == ac + bc


def get_neighbour(trajectory, point_index):
    neighbour = trajectory.get(f"neighbour{point_index}")

    if neighbour is None:
        point_pos = trajectory.data.splines[0].bezier_points[point_index-1].co

        for candidate_obj in bpy.data.objects:
            if candidate_obj.type == 'CURVE':
                if candidate_obj.name == trajectory.name or \
                        (candidate_obj.parent is not None):
                    continue

                for i in range(2):
                    candidate_pos = candidate_obj.data.splines[0].bezier_points[i].co

                    if point_pos + trajectory.location == candidate_pos + candidate_obj.location:
                        candidate_obj[f"neighbour{i+1}"] = trajectory
                        trajectory[f"neighbour{point_index}"] = candidate_obj
                        return candidate_obj

        return None

    return neighbour


def get_switch_side(trajectory):
    try:
        return next((c for c in trajectory.children if c.type == 'CURVE'))
    except StopIteration:
        return None


def get_switch_straight(side_trajectory):
    return side_trajectory.parent


def set_material(trajectory, material, index):
    if material is not None:
        profile_instance = get_instance(trajectory)
        if profile_instance is not None:
            profile_instance.material_slots[index].material = material

        if trajectory.scn_properties.type_ == "node:track:switch" and index == 1:
            if trajectory.parent is None:
                set_material(get_switch_side(trajectory), material, index)


def get_material(trajectory, index):
    profile_instance = get_instance(trajectory)

    if profile_instance is not None:
        return profile_instance.material_slots[index].material

    return None


