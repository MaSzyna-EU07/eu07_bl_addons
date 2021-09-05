
import bpy

from . import trajectory_builder

from .sectorizer import Sectorizer


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
    params_strings = name_parts[2].split("-")
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
    return f"TrajectoryProfileTemplate_{track_subtype}_{'-'.join(str(round(x, 3)) for x in profile_params)}_ML{mapping_length}_{trajectory_width*1000}"