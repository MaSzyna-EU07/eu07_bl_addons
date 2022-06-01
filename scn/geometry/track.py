import math

import bpy
import bmesh

from .manager import GeometryManager


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

    def get_from_entity(self, entity, default=None):
        for child in entity.children:
            if "TrackGeometry" in child.name:
                return child

        return default

    def set(self, entity, geometry):
        geometry_container = self.get_from_entity(entity)
        if geometry_container:
            old_geometry = geometry_container.data
            geometry_container.data = geometry
            self._purge_if_needed(old_geometry)
        else:
            geometry_container = bpy.data.objects.new("TrackGeometry", geometry)
            entity.users_collection[0].objects.link(geometry_container)

        geometry_container.parent = entity
        geometry_container.location = 0, 0, 0

        geometry_container.modifiers.clear()

        array_mod = geometry_container.modifiers.new('Array', type='ARRAY')
        array_mod.fit_type = 'FIT_CURVE'
        array_mod.curve = entity

        curve_mod = geometry_container.modifiers.new('Curve', type='CURVE')
        curve_mod.object = entity

        entity.data.dimensions = "3D"
        entity.data.use_stretch = True
        entity.data.use_deform_bounds = True

    def _purge_if_needed(self, geometry):
        if geometry:
            if geometry.users == 0:
                bpy.data.meshes.remove(geometry)


    def create(self, entity):
        geometry = bpy.data.meshes.new(f"{self.prefix}")
        geometry["scn_geometry_type"] = "node:track:normal"
        geometry["width"] = entity.eu07_track.width
        geometry["map1_length"] = entity.eu07_track.map1_length
        geometry["geometry_params"] = entity.eu07_track.geometry_params

        self.mesh = bmesh.new()
        self.uv_layer = self.mesh.loops.layers.uv.new()

        max_z = entity.eu07_track.geometry_params[0]
        med_y = entity.eu07_track.width / 2 + entity.eu07_track.geometry_params[1]
        max_y = med_y + entity.eu07_track.geometry_params[2]
        segment_length = entity.eu07_track.map1_length

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

        slope_uv_length = math.sqrt(entity.eu07_track.geometry_params[2] ** 2 + max_z ** 2) / entity.eu07_track.map1_length
        med_u = med_y / entity.eu07_track.map1_length
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

        self.generate_rails(entity.eu07_track.map1_length, entity.eu07_track.width)

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