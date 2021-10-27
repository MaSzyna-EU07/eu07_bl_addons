import math

import bmesh
import bpy
import eu07_tools
import scn.trajectory_tools.profile

from . import trajectory_utils


def get_trajectory_generator(trajectory_type):
    generator = None

    if trajectory_type == "normal":
        generator = TrackProfileGenerator()
    elif trajectory_type == "road":
        generator = RoadProfileGenerator()
    elif trajectory_type == "river":
        generator = RiverProfileGenerator()

    return generator


class TrajectoryBuilder:
    def __init__(self):
        self.default_node_track = eu07_tools.scn.create_element("node:track")

    def build_trajectory(self, node_track):
        trajectory = bpy.data.objects.new(node_track.name, bpy.data.curves.new(node_track.name, 'CURVE'))
        trajectory.data.dimensions = "3D"
        trajectory.data.use_stretch = True
        trajectory.data.use_deform_bounds = True
        trajectory.location = node_track.p1.swizzled()

        trajectory.scn_properties.type_ = node_track.type + ":" + node_track.subtype
        trajectory.scn_properties.node_max_distance = node_track.max_distance
        trajectory.scn_properties.node_min_distance = node_track.min_distance
        trajectory.scn_properties.trajectory_width = node_track.width
        trajectory.scn_properties.trajectory_friction = node_track.friction
        trajectory.scn_properties.trajectory_sound_distance = node_track.sound_distance
        trajectory.scn_properties.trajectory_quality = node_track.quality_flag
        trajectory.scn_properties.trajectory_damage = node_track.damage_flag
        trajectory.scn_properties.trajectory_environment = node_track.environment
        trajectory.scn_properties.trajectory_visible = node_track.is_visible
        trajectory.scn_properties.trajectory_mapping_length = node_track.mapping_length
        # trajectory_tools.scn_properties.trajectory_p1_roll = node_track.p1_roll
        # trajectory_tools.scn_properties.trajectory_p2_roll = node_track.p2_roll
        trajectory.scn_properties.trajectory_event0 = node_track.event0
        trajectory.scn_properties.trajectory_event1 = node_track.event1
        trajectory.scn_properties.trajectory_event2 = node_track.event2
        trajectory.scn_properties.trajectory_eventall0 = node_track.eventall0
        trajectory.scn_properties.trajectory_eventall1 = node_track.eventall1
        trajectory.scn_properties.trajectory_eventall2 = node_track.eventall2
        trajectory.scn_properties.trajectory_isolated = node_track.isolated
        trajectory.scn_properties.trajectory_overhead = node_track.overhead
        trajectory.scn_properties.trajectory_angle1 = node_track.angle1
        trajectory.scn_properties.trajectory_angle2 = node_track.angle2
        trajectory.scn_properties.trajectory_fouling1 = node_track.fouling1
        trajectory.scn_properties.trajectory_fouling2 = node_track.fouling2
        trajectory.scn_properties.trajectory_vradius = node_track.vradius
        trajectory.scn_properties.trajectory_railprofile = node_track.railprofile
        trajectory.scn_properties.trajectory_friction_memcell_name = node_track.friction_memcell_name

        return trajectory

    def create_spline(self, obj, p1, cv1, p2, cv2, p1_roll, p2_roll):
        spline = obj.data.splines.new('BEZIER')
        spline.use_smooth = False

        spline.bezier_points.add(1)
        spline.bezier_points[0].co = (0, 0, 0)
        spline.bezier_points[0].handle_left = (0, 0, 0)
        spline.bezier_points[0].handle_right = cv1.swizzled()

        p2 = p2 - p1
        spline.bezier_points[1].co = p2.swizzled()
        spline.bezier_points[1].handle_right = p2.swizzled()
        spline.bezier_points[1].handle_left = (p2 + cv2).swizzled()

        return spline


class TrajectoryProfileGenerator:
    def __init__(self):
        self.object = None
        self.mesh = None
        self.uv_layer = None
        self.typename = ""

    def generate_profile(self, track_subtype, profile_params, trajectory_width, mapping_length=6):
        name = scn.trajectory_tools.profile.profile_name(track_subtype, profile_params, trajectory_width, mapping_length)
        self.object = bpy.data.objects.new(name, bpy.data.meshes.new(name))
        collection = bpy.data.collections.get("Templates") or bpy.data.collections.new("Templates")
        collection.objects.link(self.object)

        for i in range(2 - len(self.object.material_slots)):
            self.object.data.materials.append(None)
            self.object.material_slots[i].link = 'OBJECT'

        array_mod = self.object.modifiers.new('Array', type='ARRAY')
        array_mod.fit_type = 'FIT_CURVE'
        curve_mod = self.object.modifiers.new('Curve', type='CURVE')

        self.mesh = bmesh.new()
        self.uv_layer = self.mesh.loops.layers.uv.new()

        self._build_mesh(profile_params, trajectory_width, mapping_length)

        self.mesh.to_mesh(self.object.data)
        self.mesh.free()

        return self.object

    def _build_mesh(self, profile_params, trajectory_width, mapping_length):
        pass

    def _make_faces(self, verts, uvs, material_index, num_faces, flip_normal=False):
        for i in range(num_faces):
            vindex_start, vindex_end = i * 2, i * 2 + 4
            face_verts = verts[vindex_start:vindex_end]
            face_uvs = uvs[vindex_start:vindex_end]

            # flipping vert order to generate a face with normal pointing outwards
            face_verts[:2] = reversed(face_verts[:2])
            face_uvs[:2] = reversed(face_uvs[:2])

            face = self.mesh.faces.new(face_verts)
            face.material_index = material_index

            for vertex_index, loop in enumerate(face.loops):
                loop[self.uv_layer].uv = face_uvs[vertex_index]

            if flip_normal:
                face.normal_flip()


class TrackProfileGenerator(TrajectoryProfileGenerator):
    def __init__(self):
        super().__init__()

    def _build_mesh(self, profile_params, trajectory_width, mapping_length=6):
        max_z = profile_params[0]
        med_y = trajectory_width / 2 + profile_params[1]
        max_y = med_y + profile_params[2]
        segment_length = mapping_length

        verts = [
            self.mesh.verts.new((-segment_length / 2, max_y, -max_z)),
            self.mesh.verts.new((segment_length / 2, max_y, -max_z)),
            self.mesh.verts.new((-segment_length / 2, med_y, 0)),
            self.mesh.verts.new((segment_length / 2, med_y, 0)),
            self.mesh.verts.new((-segment_length / 2, -med_y, 0)),
            self.mesh.verts.new((segment_length / 2, -med_y, 0)),
            self.mesh.verts.new((-segment_length / 2, -max_y, -max_z)),
            self.mesh.verts.new((segment_length / 2, -max_y, -max_z)),
        ]

        slope_uv_length = math.sqrt(profile_params[2] ** 2 + max_z ** 2) / mapping_length
        med_u = med_y / mapping_length
        max_u = slope_uv_length + med_u

        verts_uv = [
            (0.5 + max_u, 0),
            (0.5 + max_u, 1),
            (med_u + 0.5, 0),
            (med_u + 0.5, 1),
            (0.5 - med_u, 0),
            (0.5 - med_u, 1),
            (0.5 - max_u, 0),
            (0.5 - max_u, 1)
        ]

        self._make_faces(verts, verts_uv, 1, 3)

        self.generate_rails(mapping_length, trajectory_width)

    def generate_rails(self, mapping_length, trajectory_width):
        height = 0.172
        width = 0.067

        # u coordinates


        for rail_index in range(2):
            sideY = -1 if rail_index == 1 else 1

            minY = trajectory_width / 2 * sideY
            maxY = minY + width * sideY
            maxX = mapping_length / 2

            verts = [
                self.mesh.verts.new((-maxX, maxY, 0)),
                self.mesh.verts.new((maxX, maxY, 0)),
                self.mesh.verts.new((-maxX, maxY, height)),
                self.mesh.verts.new((maxX, maxY, height)),
                self.mesh.verts.new((-maxX, minY, height)),
                self.mesh.verts.new((maxX, minY, height)),
                self.mesh.verts.new((-maxX, minY, 0)),
                self.mesh.verts.new((maxX, minY, 0)),
            ]

            uvs_co = [
                (0.1, 0),
                (0.1, 1),
                (0.344, 0),
                (0.344, 1),
                (0.689, 0),
                (0.689, 1),
                (0.9, 0),
                (0.9, 1)
            ]

            flip = True if sideY == -1 else False

            self._make_faces(verts, uvs_co, 0, 3, flip)



class RoadProfileGenerator(TrajectoryProfileGenerator):
    def __init__(self):
        super().__init__()

    def _build_mesh(self, profile_params, trajectory_width, mapping_length=6):
        max_z, side_width, slope_width = profile_params
        surface_max_y = trajectory_width / 2
        segment_length = mapping_length

        # generate road surface
        verts = [
            self.mesh.verts.new((-segment_length / 2, surface_max_y, 0)),
            self.mesh.verts.new((segment_length / 2, surface_max_y, 0)),
            self.mesh.verts.new((-segment_length / 2, -surface_max_y, 0)),
            self.mesh.verts.new((segment_length / 2, -surface_max_y, 0)),
        ]

        slope_uv_length = math.sqrt(profile_params[2] ** 2 + max_z ** 2) / mapping_length
        med_u = surface_max_y / mapping_length
        max_u = slope_uv_length + med_u

        verts_uv = [
            (0.5 + med_u, 0),
            (0.5 + med_u, 1),
            (0.5 - med_u, 0),
            (0.5 - med_u, 1),
        ]

        self._make_faces(verts, verts_uv, 0, 1)

        # generate side of the road

        if max_z < 0:
            left_sidewalk_width = side_width
            right_sidewalk_width = slope_width

            for side_index in range(2):
                sideY = -1 if side_index == 1 else 1

                sidewalk_width = left_sidewalk_width if sideY == 1 else right_sidewalk_width

                if sidewalk_width == 0:
                    continue

                slope_factor = 1 / 3.75

                sidewalk_begin_y = surface_max_y * sideY
                sidewalk_edge_end_y = (surface_max_y + (slope_factor * abs(max_z))) * sideY
                sidewalk_end_y = (abs(sidewalk_edge_end_y) + sidewalk_width) * sideY

                verts = [
                    self.mesh.verts.new((segment_length / 2, sidewalk_begin_y, 0)),
                    self.mesh.verts.new((-segment_length / 2, sidewalk_begin_y, 0)),
                    self.mesh.verts.new((segment_length / 2, sidewalk_edge_end_y, -max_z)),
                    self.mesh.verts.new((-segment_length / 2, sidewalk_edge_end_y, -max_z)),
                    self.mesh.verts.new((segment_length / 2, sidewalk_end_y, -max_z)),
                    self.mesh.verts.new((-segment_length / 2, sidewalk_end_y, -max_z)),
                ]

                u_coord = 0.515625 if sideY == 1 else 0.484375

                verts_uv = [
                    (0, 0),
                    (0, 1),
                    (u_coord + slope_factor * abs(max_z), 0),
                    (u_coord + slope_factor * abs(max_z), 1),
                    (u_coord, 0),
                    (u_coord, 1)
                ]

                flip = True if sideY == -1 else False
                self._make_faces(verts, verts_uv, 1, 2, flip)
        else:

            for side_index in range(2):
                sideY = -1 if side_index == 1 else 1

                side_med_y = (surface_max_y + side_width) * sideY
                side_max_y = (surface_max_y + side_width + slope_width) * sideY


                verts = [
                    self.mesh.verts.new((-segment_length / 2, side_max_y, -max_z)),
                    self.mesh.verts.new((segment_length / 2, side_max_y, -max_z)),
                    self.mesh.verts.new((-segment_length / 2, side_med_y, 0)),
                    self.mesh.verts.new((segment_length / 2, side_med_y, 0)),
                    self.mesh.verts.new((-segment_length / 2, surface_max_y * sideY, 0)),
                    self.mesh.verts.new((segment_length / 2, surface_max_y * sideY, 0))
                ]

                verts_uv = [
                    (0, 0),
                    (0, 1),
                    (0.5, 0),
                    (0.5, 1),
                    (1, 0),
                    (1, 1)
                ]

                flip = True if sideY == -1 else False
                self._make_faces(verts, verts_uv, 1, 2, flip)


class RiverProfileGenerator(TrajectoryProfileGenerator):
    def __init__(self):
        super().__init__()

    def _build_mesh(self, profile_params, trajectory_width, mapping_length=6):
        max_z = profile_params[0]
        med_y = trajectory_width / 2
        max_y = med_y + profile_params[2]
        segment_length = mapping_length

        verts = [
            self.mesh.verts.new((-segment_length / 2, med_y, 0)),
            self.mesh.verts.new((segment_length / 2, med_y, 0)),
            self.mesh.verts.new((-segment_length / 2, -med_y, 0)),
            self.mesh.verts.new((segment_length / 2, -med_y, 0)),
        ]

        slope_uv_length = math.sqrt(profile_params[2] ** 2 + max_z ** 2) / mapping_length
        med_u = med_y / mapping_length
        max_u = slope_uv_length + med_u

        verts_uv = [
            (0.5 + med_u, 0),
            (0.5 + med_u, 1),
            (0.5 - med_u, 0),
            (0.5 - med_u, 1),
        ]

        self._make_faces(verts, verts_uv, 0, 1)

        for side_index in range(2):
            sideY = -1 if side_index == 1 else 1

            verts = [
                self.mesh.verts.new((-segment_length / 2, med_y * sideY, 0)),
                self.mesh.verts.new((segment_length / 2, med_y * sideY, 0)),
                self.mesh.verts.new((-segment_length / 2, max_y * sideY, max_z)),
                self.mesh.verts.new((segment_length / 2, max_y * sideY, max_z)),
            ]

            verts_uv = [
                (1, 0),
                (1, 1),
                (0, 0),
                (0, 1),
            ]

            flip = True if sideY == 1 else False
            self._make_faces(verts, verts_uv, 1, 1, flip)
