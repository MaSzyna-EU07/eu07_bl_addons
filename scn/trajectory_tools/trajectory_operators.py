import bpy
from bpy_extras import view3d_utils

import scn.trajectory_tools.profile
from . import  trajectory_utils
from . import trajectory_builder
from . import profile


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


class AddTrackOperator(bpy.types.Operator):
    bl_idname = "scn.add_track"
    bl_label = "Add Track"

    def execute(self, context):
        return {'FINISHED'}

    def modal(self, context, event):
        region = context.region
        region_data = context.space_data.region_3d
        self.mouse_pos = event.mouse_region_x, event.mouse_region_y

        # TODO: Separate control point configuration?

        view_origin = view3d_utils.region_2d_to_origin_3d(region, region_data, self.mouse_pos)
        direction = view3d_utils.region_2d_to_vector_3d(region, region_data, self.mouse_pos)

        cv_offset = self.track_spline.calc_length(resolution=1) / 3

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if self.point_counter == 0:
                self.p1.co = view_origin + (direction * 100)
                self.p1.handle_left_type = 'FREE'
                self.p1.handle_right_type = 'FREE'
                self.p1.handle_left = self.p1.co
                self.p1.handle_right = self.p1.co
                self.point_counter += 1
                self.p2.handle_left_type = 'FREE'
                self.p2.handle_right_type = 'FREE'
                self.p2.co = view_origin + (direction * 100)
                self.p2.handle_left = self.p2.co
                self.p2.handle_right = self.p2.co
                self.p2.hide = False
            elif self.point_counter == 1:
                self.track_object.scn_properties.type_ = 'node:track:normal'
                return {'FINISHED'}

        elif event.type == 'MOUSEMOVE' and self.point_counter == 1:
            self.p2.co = view_origin + (direction * 100)

            cv_offset = self.track_spline.calc_length(resolution=1) / 3

            self.p2.handle_right = self.p2.co
            self.p2.handle_left = self.p2.co + (self.p1.co - self.p2.co).normalized() * cv_offset

            self.p1.handle_left = self.p1.co
            self.p1.handle_right = self.p1.co + (self.p2.co - self.p1.co).normalized() * cv_offset


        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.context.scene.collection.objects.unlink(self.track_object)
            bpy.data.objects.remove(self.track_object)
            bpy.data.curves.remove(self.track_curve)
            bpy.data.objects.remove(self.profile_instance)

            return {'CANCELLED'}
        else:
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.point_counter = 0
        self.track_curve = bpy.data.curves.new("Track", 'CURVE')
        self.track_spline = self.track_curve.splines.new('BEZIER')

        bpy.ops.object.select_all(action='DESELECT')
        # TODO: Track creation should be separated as util
        self.track_object = bpy.data.objects.new("Track", self.track_curve)
        context.scene.collection.objects.link(self.track_object)
        self.track_object.select_set(True)
        context.view_layer.objects.active = self.track_object

        self.track_curve.use_stretch = True
        self.track_curve.use_deform_bounds = True

        profile_gen = trajectory_builder.get_trajectory_generator("normal")
        self.profile_instance = profile_gen.generate_profile("normal", [0.2, 0.5, 1.3], 1.435)
        profile.set_instance(self.track_object, self.profile_instance)

        self.track_spline.bezier_points.add(1)
        self.track_spline.bezier_points[1].hide = True

        self.p1, self.p2 = self.track_spline.bezier_points

        self.execute(context)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}