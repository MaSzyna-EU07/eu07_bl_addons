import bpy

import scn.trajectory_tools.profile
from . import  trajectory_utils


class UpdateTrajectoryProfileOperator(bpy.types.Operator):
    bl_idname = "scn.update_trajectory_profile"
    bl_label = "Update Profile"

    def execute(self, context):
        trajectory = context.active_object
        if trajectory is not None:
            profile_params = [
                trajectory.scn_properties.trajectory_profile_param1,
                trajectory.scn_properties.trajectory_profile_param2,
                trajectory.scn_properties.trajectory_profile_param3
            ]

            track_subtype = trajectory.scn_properties.type_.split(":")[-1]
            trajectory_width = trajectory.scn_properties.trajectory_width

            old_profile = scn.trajectory_tools.profile.get_instance(trajectory)

            mat0 = old_profile.material_slots[0].material
            mat1 = old_profile.material_slots[1].material

            new_profile = scn.trajectory_tools.profile.create_instance(track_subtype, profile_params, trajectory_width)

            scn.trajectory_tools.profile.set_instance(trajectory, new_profile)

            if old_profile is not None:
                trajectory_utils.set_material(trajectory, mat0, 0)
                trajectory_utils.set_material(trajectory, mat1, 1)

        return {'FINISHED'}

