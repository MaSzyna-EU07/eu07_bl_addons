import math

import bmesh
import bpy
import eu07_tools


def generate_trajectory_profile(trajectory_type, profile_params, trajectory_width, mapping_length):
    generator = None

    if trajectory_type == "normal":
        generator = TrackProfileGenerator()
    elif trajectory_type == "road":
        generator = RoadProfileGenerator()
    elif trajectory_type == "river":
        generator = RiverProfileGenerator()

    return generator.generate_profile(trajectory_type, profile_params, trajectory_width, mapping_length)


def instantiate_trajectory_profile(track_subtype, profile_params, trajectory_width, mapping_length):
    mapping_length = 6
    name = get_profile_name(track_subtype, profile_params, trajectory_width, mapping_length)
    profile = bpy.data.objects.get(name)
    if profile is None:
        profile = generate_trajectory_profile(track_subtype, profile_params, trajectory_width, mapping_length)

    profile = profile.copy()

    return profile


def get_profile_name(track_subtype, profile_params, trajectory_width, mapping_length):
    return f"TProfile_{track_subtype}_{'-'.join(str(x) for x in profile_params)}_ML{mapping_length}_{trajectory_width}"


class TrajectoryBuilder:
    def __init__(self, config):
        self._config = config
        self.default_node_track = eu07_tools.scn.create_element("node:track")

    def build_trajectory(self, node_track):
        trajectory = bpy.data.objects.new(node_track.name, bpy.data.curves.new(node_track.name, 'CURVE'))
        trajectory.data.dimensions = "3D"
        trajectory.data.use_stretch = True
        trajectory.data.use_deform_bounds = True
        trajectory.location = eu07_tools.utils.switch_coordinate_system(node_track.p1)

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
        trajectory.scn_properties.trajectory_p1_roll = node_track.p1_roll
        trajectory.scn_properties.trajectory_p2_roll = node_track.p2_roll
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

        self._create_spline(trajectory, node_track.p1, node_track.cv1, node_track.p2, node_track.cv2)

        return trajectory

    def _create_spline(self, obj, p1, cv1, p2, cv2):
        spline = obj.data.splines.new('BEZIER')
        spline.use_smooth = False

        spline.bezier_points.add(1)
        spline.bezier_points[0].co = (0, 0, 0)
        spline.bezier_points[0].handle_left = (0, 0, 0)
        spline.bezier_points[0].handle_right = eu07_tools.utils.switch_coordinate_system(cv1)
        if cv1 == (0, 0, 0):
            spline.bezier_points[0].handle_left_type = 'AUTO'
            spline.bezier_points[0].handle_right_type = 'AUTO'

        p2 = p2 - p1
        spline.bezier_points[1].co = eu07_tools.utils.switch_coordinate_system(p2)
        spline.bezier_points[1].handle_right = eu07_tools.utils.switch_coordinate_system(p2)
        spline.bezier_points[1].handle_left = eu07_tools.utils.switch_coordinate_system(p2 + cv2)
        if cv2 == (0, 0, 0):
            spline.bezier_points[1].handle_left_type = 'AUTO'
            spline.bezier_points[1].handle_right_type = 'AUTO'

        return spline



class TrajectoryProfileGenerator:
    def __init__(self):
        self.object = None
        self.mesh = None
        self.uv_layer = None
        self.typename = ""



    def generate_profile(self, track_subtype, profile_params, trajectory_width, mapping_length):
        name = get_profile_name(track_subtype, profile_params, trajectory_width, mapping_length)
        self.object = bpy.data.objects.new(name, bpy.data.meshes.new(name))
        bpy.data.collections["Profiles"].objects.link(self.object)

        for i in range(2):
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

    def _make_faces(self, verts, uvs, material_index, num_faces):
        for i in range(num_faces):
            vindex_start, vindex_end = i * 2, i * 2 + 4
            face_verts = verts[vindex_start:vindex_end]
            face_uvs = uvs[vindex_start:vindex_end]

            face_verts[:2] = reversed(face_verts[:2])
            face_uvs[:2] = reversed(face_uvs[:2])

            face = self.mesh.faces.new(face_verts)
            face.material_index = material_index

            for vertex_index, loop in enumerate(face.loops):
                print(face_uvs[vertex_index])
                loop[self.uv_layer].uv = face_uvs[vertex_index]


class TrackProfileGenerator(TrajectoryProfileGenerator):
    def __init__(self):
        super().__init__()

    def _build_mesh(self, profile_params, trajectory_width, mapping_length):
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
        height = 0.15
        width = 0.067

        # u coordinates
        u_co = [
            0,
            0.25,
            0.65,
            1
        ]

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

            verts_uv = [
                (0, 0)
            ] * 8

            if sideY == -1:
                verts.reverse()

            self._make_faces(verts, verts_uv, 0, 3)



class RoadProfileGenerator(TrajectoryProfileGenerator):
    pass


class RiverProfileGenerator(TrajectoryProfileGenerator):
    pass
