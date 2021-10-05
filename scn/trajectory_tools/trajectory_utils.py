import math

import bpy

import eu07_tools
from common import get_path_from_material
from scn.trajectory_tools import trajectory_builder

from scn.sectorizer import Sectorizer


def create(name, location=None):
    trajectory = bpy.data.objects.new(name, bpy.data.curves.new(name, 'CURVE'))
    trajectory.data.dimensions = "3D"
    trajectory.data.use_stretch = True
    trajectory.data.use_deform_bounds = True
    if location is not None:
        trajectory.location = location

    spline = trajectory.data.splines.new('BEZIER')
    spline.use_smooth = False

    spline.bezier_points.add(1)

    return trajectory


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

    profile_instance = get_profile_instance(track_object)

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

        node.map1 = get_path_from_material(mesh.material_slots[0].material)
        node.map2 = get_path_from_material(junction_mesh.material_slots[0].material)

        node.trackbed = get_path_from_material(mesh.material_slots[1].material)
    else:
        node.geometry_params = get_profile_params(profile_instance)


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


def get_profile_params(profile_instance):
    name_parts = profile_instance.name.split("_")
    params_strings = name_parts[2].split(";")
    return [float(p) for p in params_strings]



def find_profile(track_subtype, profile_params, trajectory_width, mapping_length=6):
    return bpy.data.objects.get(profile_name(track_subtype, profile_params, trajectory_width, mapping_length))


def create_profile_instance(track_subtype, profile_params, trajectory_width, mapping_length=6):
    name = profile_name(track_subtype, profile_params, trajectory_width, mapping_length)
    profile = bpy.data.objects.get(name)
    if profile is None:
        generator = trajectory_builder.get_trajectory_generator(track_subtype)
        profile = generator.generate_profile(track_subtype, profile_params, trajectory_width, mapping_length)

    profile = profile.copy()

    return profile


def get_profile_instance(trajectory):
    try:
        return next((c for c in trajectory.children if c.name.startswith("TrajectoryProfileTemplate")))
    except StopIteration:
        return None


def copy_profile_instance(source, dest):
    profile = get_profile_instance(source)
    print(f"Copying profile from {source.name} to {dest.name}")
    set_profile_instance(dest, profile.copy())


def set_profile_instance(trajectory, new_profile_instance):
    unset_profile_instance(trajectory)

    Sectorizer.auto_put(new_profile_instance)

    new_profile_instance.parent = trajectory
    new_profile_instance.location = (0, 0, 0)
    new_profile_instance.hide_select = True
    new_profile_instance.modifiers["Array"].curve = trajectory
    new_profile_instance.modifiers["Curve"].object = trajectory


def unset_profile_instance(trajectory):
    old_profile_instance = get_profile_instance(trajectory)

    if old_profile_instance is not None:

        is_last_user = old_profile_instance.data.users == 2
        if is_last_user:
            # this is problemtaic!
            original_instance = bpy.data.objects.get(old_profile_instance.data.name)
            bpy.data.objects.remove(original_instance)

        bpy.data.objects.remove(old_profile_instance)


def set_material(trajectory, material, index):
    if material is not None:
        profile_instance = get_profile_instance(trajectory)
        if profile_instance is not None:
            profile_instance.material_slots[index].material = material

        if trajectory.scn_properties.type_ == "node:track:switch" and index == 1:
            if trajectory.parent is None:
                set_material(get_switch_side(trajectory), material, index)


def get_material(trajectory, index):
    profile_instance = get_profile_instance(trajectory)

    if profile_instance is not None:
        return profile_instance.material_slots[index].material

    return None


def profile_name(track_subtype, profile_params, trajectory_width, mapping_length):
    return f"TrajectoryProfileTemplate_{track_subtype}_{';'.join(str(round(x, 3)) for x in profile_params)}_ML{mapping_length}_{trajectory_width*1000}"