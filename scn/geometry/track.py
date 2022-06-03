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


def interpolate(x1: float, x2: float, y1: float, y2: float, x: float):
    return ((y2 - y1) * x + x2 * y1 - x1 * y2) / (x2 - x1)


# TODO: Link objects more accurately
class TrackNormalGeometryManager(GeometryManager):
    def __init__(self):
        super().__init__()
        self.type = "node:track:normal"

    def get(self, entity):
        for mesh in bpy.data.meshes:
            if mesh["scn_geometry_type"] == self.type:
                if (
                    mesh["width"] == entity.eu07_track.width and
                    mesh["map1_length"] == entity.eu07_track.map1_length and
                    mesh["geometry_params"] == entity.eu07_track.geometry_params
                ):
                    return mesh
        else:
            return self.create(entity)

    def get_container_from(self, entity, default=None):
        for child in entity.children:
            if "TrackGeometry" in child.name:
                return child

        return default

    def set(self, entity, geometry):
        geometry_container = self.get_container_from(entity)
        if geometry_container:
            old_geometry = geometry_container.data
            geometry_container.data = geometry
            self._purge_if_needed(old_geometry)
        else:
            geometry_container = bpy.data.objects.new("TrackGeometry", geometry)
            entity.users_collection[0].objects.link(geometry_container)

        curve_mod = geometry_container.modifiers.new('Curve', type='CURVE')
        curve_mod.object = entity

        geometry_container.location = entity.location
        geometry_container.parent = entity

        geometry_container.modifiers.clear()

        

        entity.data.dimensions = "3D"
        entity.data.use_stretch = True
        entity.data.use_deform_bounds = True

    def _purge_if_needed(self, geometry):
        if geometry:
            if geometry.users == 0:
                bpy.data.meshes.remove(geometry)



    def create_mesh(self, length, profile1, profile2, fidelity=1):
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
            for vertA, vertB in zip(profileA, profileB):
                coA, uvA = vertA
                coB, uvB = vertB
                p_verts.extend((
                    self.mesh.verts.new(coA), 
                    self.mesh.verts.new(coB)
                ))
                p_uvs.extend((uvA, uvB))

            self._make_faces(p_verts, p_uvs, 0, 4)


    
    def interpolate_profiles(self, profile1, profile2, x):
        x = 1 if x > 1 else x

        output = []

        for vert1, vert2 in zip(profile1, profile2):
            co1, co2 = mathutils.Vector(vert1[0]), mathutils.Vector(vert2[0])

            co_out = co1.lerp(co2, x)

            print(co_out)

            vert_data = (
                co_out,
                (0, 0)
            )

            output.append(vert_data)

        print("----")

        return output           



    def create_profile(self, entity, roll, yOffset=0):
        width = entity.eu07_track.width
        htw = width * 0.5
        height, side, slope = entity.eu07_track.geometry_params
        span = htw + side + slope
        rail_height = 0.18 #TODO: Grab from profile
        total_height = height + rail_height
        med_x = htw + side

        sin = math.sin(math.radians(roll))
        cos = math.cos(math.radians(roll))

        output = (
            (
                (-span, yOffset, -total_height),
                (0, 0)
            ),
            (
                (-(med_x * cos), yOffset, -med_x * sin - rail_height),
                (0, 0)
            ),
            (
                (0, yOffset, -rail_height + 0.01),
                (0, 0)
            ),
            (
                (med_x * cos, yOffset, med_x * sin - rail_height),
                (0, 0)
            ),
            (
                (span, yOffset, -total_height),
                (0, 0)
            )
        )

        return output


    def create(self, entity):
        geometry = bpy.data.meshes.new(f"{self.prefix}")
        geometry["scn_geometry_type"] = "node:track:normal"
        geometry["width"] = entity.eu07_track.width
        geometry["map1_length"] = entity.eu07_track.map1_length
        geometry["geometry_params"] = entity.eu07_track.geometry_params

        self.mesh = bmesh.new()
        self.uv_layer = self.mesh.loops.layers.uv.new()

        profile1 = self.create_profile(entity, entity.eu07_track.p1_roll)
        # TODO: Guess why we need to negate yOffset?
        profile2 = self.create_profile(entity, entity.eu07_track.p2_roll, -entity.eu07_track.length)
        self.create_mesh(entity.eu07_track.length, profile1, profile2)

        #self.generate_rails(entity.eu07_track.map1_length, entity.eu07_track.width)

        self.mesh.to_mesh(geometry)
        self.mesh.free()

        return geometry

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