import bpy

from scn.sectorizer import Sectorizer
from scn.trajectory_tools import trajectory_builder


def get_params(profile_instance):
    name_parts = profile_instance.name.split("_")
    params_strings = name_parts[2].split(";")
    return [float(p) for p in params_strings]


def find(track_subtype, profile_params, trajectory_width, mapping_length=6):
    return bpy.data.objects.get(profile_name(track_subtype, profile_params, trajectory_width, mapping_length))


def create_instance(track_subtype, profile_params, trajectory_width, mapping_length=6):
    name = profile_name(track_subtype, profile_params, trajectory_width, mapping_length)
    profile = bpy.data.objects.get(name)
    if profile is None:
        generator = trajectory_builder.get_trajectory_generator(track_subtype)
        profile = generator.generate_profile(track_subtype, profile_params, trajectory_width, mapping_length)

    profile = profile.copy()

    return profile


def get_instance(trajectory):
    try:
        return next((c for c in trajectory.children if c.name.startswith("TrajectoryProfileTemplate")))
    except StopIteration:
        return None


def copy_instance_between(source, dest):
    profile = get_instance(source)
    set_instance(dest, profile.copy())


def set_instance(trajectory, new_profile_instance):
    unset_instance(trajectory)

    new_profile_instance.parent = trajectory
    new_profile_instance.location = (0, 0, 0)
    new_profile_instance.hide_select = True
    new_profile_instance.modifiers["Array"].curve = trajectory
    new_profile_instance.modifiers["Curve"].object = trajectory

    Sectorizer.insert_into_sector(
        new_profile_instance,
        Sectorizer.get_sector_by_location(trajectory.location)
    )


def unset_instance(trajectory):
    old_profile_instance = get_instance(trajectory)

    if old_profile_instance is not None:

        is_last_user = old_profile_instance.data.users == 2
        if is_last_user:
            # this is problemtaic!
            original_instance = bpy.data.objects.get(old_profile_instance.data.name)
            bpy.data.objects.remove(original_instance)

        bpy.data.objects.remove(old_profile_instance)


def profile_name(track_subtype, profile_params, trajectory_width, mapping_length):
    return f"TrajectoryProfileTemplate_{track_subtype}_{';'.join(str(round(x, 3)) for x in profile_params)}_ML{mapping_length}_{trajectory_width*1000}"