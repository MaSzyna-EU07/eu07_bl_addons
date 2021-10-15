import bpy
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

            old_profile = trajectory_utils.get_profile_instance(trajectory)

            mat0 = old_profile.material_slots[0].material
            mat1 = old_profile.material_slots[1].material

            new_profile = trajectory_utils.create_profile_instance(track_subtype, profile_params, trajectory_width)

            trajectory_utils.set_profile_instance(trajectory, new_profile)

            if old_profile is not None:
                trajectory_utils.set_material(trajectory, mat0, 0)
                trajectory_utils.set_material(trajectory, mat1, 1)

        return {'FINISHED'}


class AddTrackOperator(bpy.types.Operator):
    bl_label = "Add Track"


    def execute(self, context):
        return {'FINISHED'}

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            self.execute(context)
        elif event.type == 'LEFTMOUSE':

            return {'FINISHED'}
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            pass

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):

        self.execute(context)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}