import math

import bpy
import bmesh
import mathutils

from .manager import GeometryManager




def create_track_geometry_manager(obj):
    if obj.eu07_track.type == "normal":
        return TrackNormalGeometryManager()
    else:
        raise ValueError(f"{obj.eu07_track.type} is not valid trajectory type or Geometry Manager is not implemented.")



# TODO: Link objects more accurately
class TrackNormalGeometryManager(GeometryManager):
    def __init__(self):
        super().__init__()
        self.type = "node:track:normal"

    # TODO: This is problematic while duplicating curves - geometry container reference is shared...
    def get(self, entity):
        container = self.get_container_from(entity)
        return container.data if container else self.create(entity)

    def get_container_from(self, entity, default=None):
        for obj in entity.children:
            if "TrackGeometry" in obj.name:
                return obj

    def set(self, entity, geometry):
        # TODO: Move limit scale to better place
        limit_scale = entity.constraints.new("LIMIT_SCALE")
        limit_scale.use_max_x, limit_scale.use_max_y, limit_scale.use_max_z = True, True, True
        limit_scale.use_min_x, limit_scale.use_min_y, limit_scale.use_min_z = True, True, True
        limit_scale.use_transform_limit = True
        limit_scale.max_x, limit_scale.max_y, limit_scale.max_z = 1, 1, 1
        limit_scale.min_x, limit_scale.min_y, limit_scale.min_z = 1, 1, 1

        geometry_container = self.get_container_from(entity)
        if geometry_container:
            old_geometry = geometry_container.data
            geometry_container.data = geometry
            self._purge_if_needed(old_geometry)
        else:
            geometry_container = bpy.data.objects.new(f"TrackGeometry({entity.name})", geometry)

            bpy.context.scene.collection.objects.link(geometry_container)
            geometry_container.parent = entity

            curve_mod = geometry_container.modifiers.new('Curve', type='CURVE')
            curve_mod.object = entity

            entity.data.dimensions = "3D"
            entity.data.use_stretch = True
            entity.data.use_deform_bounds = True

            #geometry_container.hide_select = True

            copy_location = geometry_container.constraints.new("COPY_LOCATION")
            copy_location.target = entity
            copy_location.use_x, copy_location.use_y, copy_location.use_z = True, True, True

            copy_rotation = geometry_container.constraints.new("COPY_ROTATION")
            copy_rotation.target = entity
            copy_rotation.use_x, copy_rotation.use_y, copy_rotation.use_z = True, True, True

    def _purge_if_needed(self, geometry):
        if geometry:
            if geometry.users == 0:
                bpy.data.meshes.remove(geometry)

    def create(self, entity):
        geometry = bpy.data.meshes.new(f"{self.prefix}")

        self.mesh = bmesh.new()
        self.uv_layer = self.mesh.loops.layers.uv.new()

        profile1 = self.create_profile(entity, entity.eu07_track.p1_roll)
        # TODO: Guess why we need to negate yOffset?
        profile2 = self.create_profile(entity, entity.eu07_track.p2_roll, -entity.eu07_track.length)
        self.create_mesh(entity.eu07_track.length, profile1, profile2)

        #TODO: Why i must pass negative value of rolls? That's bad :(
        if entity.eu07_track.material1:
            right_rail1 = self.create_rail_profile(entity, -entity.eu07_track.p1_roll)
            right_rail2 = self.create_rail_profile(entity, -entity.eu07_track.p2_roll, -entity.eu07_track.length)
            self.create_mesh(entity.eu07_track.length, right_rail1, right_rail2, num_faces=len(right_rail1) - 1, material_index=0)

            left_rail1 = self.create_rail_profile(entity, -entity.eu07_track.p1_roll, side=-1)
            left_rail2 = self.create_rail_profile(entity, -entity.eu07_track.p2_roll, -entity.eu07_track.length, side=-1)
            self.create_mesh(entity.eu07_track.length, left_rail1, left_rail2, num_faces=len(right_rail1) - 1, material_index=0)

        self.mesh.to_mesh(geometry)
        self.mesh.free()

        return geometry

    def create_mesh(self, length, profile1, profile2, fidelity=1, num_faces=4, material_index=1):
        segment_length = 2 / fidelity
        step = segment_length / length
        num_segments = math.ceil(length / segment_length) + 1

        profiles = []

        for i in range(num_segments):
            profile_interpolated = self.interpolate_profiles(profile1, profile2, i * step)
            profiles.append(profile_interpolated)

 
        for segment_index in range(num_segments-1):
            p_verts = []
            p_uvs = []
            profileA, profileB = profiles[segment_index], profiles[segment_index+1]
            for pointA, pointB in zip(profileA, profileB):
                locA, nrmA, uvA = pointA[:3], pointA[3:6], pointA[6:8]
                locB, nrmB, uvB = pointB[:3], pointB[3:6], pointB[6:8]

                print(locA)
                p_verts.extend((
                    self.mesh.verts.new(locA), 
                    self.mesh.verts.new(locB)
                ))
                p_uvs.extend((uvA, uvB))

            self._make_faces(p_verts, p_uvs, material_index, num_faces)

    def interpolate_profiles(self, profile1, profile2, x):
        x = 1 if x > 1 else x

        output = []

        for vert1, vert2 in zip(profile1, profile2):
            co1, co2 = mathutils.Vector(vert1[:3]), mathutils.Vector(vert2[:3])

            co_out = co1.lerp(co2, x)

            vert_data = [
                *co_out,
                0, 0, 1,
                0, 0
            ]

            output.append(vert_data)

        return output

    def create_profile(self, entity, roll, xOffset=0):
        width = entity.eu07_track.width
        htw = width * 0.5
        height, side, slope = entity.eu07_track.geometry_params
        span = htw + side + slope
        rail_height = 0.18 #TODO: Grab from profile
        total_height = height + rail_height
        med_y = htw + side

        sin = math.sin(math.radians(roll))
        cos = math.cos(math.radians(roll))

        output = [
            [
                xOffset, -span, -total_height,
                0, 0, 1,
                0, 0,
            ],
            [
                xOffset, -(med_y * cos), -med_y * sin - rail_height,
                0, 0, 1,
                0, 0
            ],
            [
                xOffset, 0, -rail_height + 0.01,
                0, 0, 1,
                0, 0
            ],
            [
                xOffset, med_y * cos, med_y * sin - rail_height,
                0, 0, 1,
                0, 0
            ],
            [
                xOffset, span, -total_height,
                0, 0, 1,
                0, 0
            ]
        ]

        return output


    def calc_ballast_uv(self, mapping_length, tex_ratio=1, xOffset=0):
        if mapping_length == 4:
            return [
                [0, 0],
                [0.33, 0],
                [0.5, 0],
                [0.67, 0],
                [1, 0]
            ]

        else:
            # NOTE: This code is highly inspired by Track.cpp from EU07 source code
            max = tex_ratio * mapping_length

    def create_rail_profile(self, entity, roll, xOffset=0, side=1):
        profile_bank = bpy.context.scene.eu07_rail_profile_bank

        profile_data = profile_bank.get(entity.eu07_track.railprofile)
        if not profile_data:
            profile_data = profile_bank.add_from_name(entity.eu07_track.railprofile)

        htw = entity.eu07_track.width / 2
        sin = math.sin(math.radians(roll))
        cos = math.cos(math.radians(roll))

        output = []

        for i, point in enumerate(profile_data.rail_points):

            # TODO: Fix normals and UV
            output.append(
                [
                    xOffset,
                    (htw + point.location[0]) * side * cos + point.location[1] * sin,
                    -(htw + point.location[0]) * side * sin + point.location[1] * cos,
                    1,
                    point.normal[0],
                    point.normal[1],
                    point.mapping,
                    point.mapping
                ]
            )

        return output