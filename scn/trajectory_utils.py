
import bpy

from . import trajectory_builder


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
        return next((c for c in trajectory.children if c.name.startswith("TProfile")))
    except StopIteration:
        return None


def set_profile_instance(trajectory, new_profile_instance):
    unset_profile_instance(trajectory)

    new_profile_instance.parent = trajectory
    new_profile_instance.location = (0, 0, 0)
    new_profile_instance.hide_select = True
    new_profile_instance.modifiers["Array"].curve = trajectory
    new_profile_instance.modifiers["Curve"].object = trajectory


def unset_profile_instance(trajectory):
    old_profile_instance = get_profile_instance(trajectory)

    if old_profile_instance is not None:

        is_last_user = len(old_profile_instance.data.users == 2)
        if is_last_user:
            original_instance = bpy.data.objects.get(old_profile_instance.data.name)
            bpy.data.objects.remove(original_instance)

        bpy.data.objects.remove(old_profile_instance)


def set_material(trajectory, material, index):
    if material is None:
        return
    profile_instance = get_profile_instance(trajectory)
    profile_instance.material_slots[index].material = material


def get_material(trajectory, index):
    profile_instance = get_profile_instance(trajectory)

    if profile_instance is not None:
        return profile_instance.material_slots[index].material

    return None


def profile_name(track_subtype, profile_params, trajectory_width, mapping_length):
    return f"TProfile_{track_subtype}_{'-'.join(str(x) for x in profile_params)}_ML{mapping_length}_{trajectory_width}"
