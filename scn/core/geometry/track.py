import abc
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
        self.prefix = "TrackGeometry"

    def get(self, obj):
        container = self.get_container_from(obj)
        return container.data if container else self.create(obj)

    def get_container_from(self, obj, default=None):
        for child in obj.children:
            if "TrackGeometry" in child.name:
                return child

    def set(self, obj, mesh_data):
        # TODO: Move constrains setup to better place
        # limit_scale = obj.constraints.new("LIMIT_SCALE")
        # limit_scale.use_max_x, limit_scale.use_max_y, limit_scale.use_max_z = True, True, True
        # limit_scale.use_min_x, limit_scale.use_min_y, limit_scale.use_min_z = True, True, True
        # limit_scale.use_transform_limit = True
        # limit_scale.max_x, limit_scale.max_y, limit_scale.max_z = 1, 1, 1
        # limit_scale.min_x, limit_scale.min_y, limit_scale.min_z = 1, 1, 1

        geometry_container = self.get_container_from(obj)
        if geometry_container:
            old_geometry = geometry_container.data
            geometry_container.data = mesh_data
            self._purge_if_needed(old_geometry)
        else:
            geometry_container = bpy.data.objects.new(f"TrackGeometry({obj.name})", mesh_data)

            bpy.context.scene.collection.objects.link(geometry_container)
            geometry_container.parent = obj

            curve_mod = geometry_container.modifiers.new('Curve', type='CURVE')
            curve_mod.object = obj

            obj.data.dimensions = "3D"
            obj.data.use_stretch = True
            obj.data.use_deform_bounds = True

            #geometry_container.hide_select = True

            copy_location = geometry_container.constraints.new("COPY_LOCATION")
            copy_location.target = obj
            copy_location.use_x, copy_location.use_y, copy_location.use_z = True, True, True

            copy_rotation = geometry_container.constraints.new("COPY_ROTATION")
            copy_rotation.target = obj
            copy_rotation.use_x, copy_rotation.use_y, copy_rotation.use_z = True, True, True

    def create(self, obj):
        entity_props = obj.eu07_track

        # TODO: Get profile from neighbours in case of transition
        height1, side1, slope1 = entity_props.geometry_params
        height2, side2, slope2 = entity_props.geometry_params

        profile_p1 = TrapezoidProfile(height1, side1, slope1, entity_props.width, entity_props.p1_roll)
        builder1 = CrossSectionBuilderNormal()
        builder1.build_cross_section(profile_p1, x_offset=0)
        builder1.build_uv(profile_p1, 0, map_length=entity_props.map1_length, tex_ratio=1)
        cross_section1 = builder1.finish()

        profile_p2 = TrapezoidProfile(height2, side2, slope2, entity_props.width, entity_props.p2_roll)
        builder2 = CrossSectionBuilderNormal()
        builder2.build_cross_section(profile_p2, x_offset=entity_props.length)
        builder2.build_uv(profile_p2, entity_props.length, map_length=entity_props.map1_length, tex_ratio=1, )
        cross_section2 = builder2.finish()

        mesh_data = bpy.data.meshes.new(f"{self.prefix}")
        mesh_maker = MeshMaker(mesh_data, entity_props.length)
        mesh_maker.extrude_between(cross_section1, cross_section2, material_index=1)
        mesh_maker.finish()

        return mesh_data

    def _purge_if_needed(self, geometry):
        if geometry:
            if geometry.users == 0:
                bpy.data.meshes.remove(geometry)

# TODO: ROLLFIX!


class TrapezoidProfile:
    def __init__(self, height, side, slope, width, roll):
        self.height = height
        self.side = side
        self.slope = slope
        self.width = width
        self.roll = roll

    @property
    def htw(self):
        return self.width / 2

    @property
    def outer_span(self):
        return self.htw + self.side + self.slope

    @property
    def mid_span(self):
        return self.htw + self.side

    @property
    def sin(self):
        return math.sin(math.radians(self.roll))

    @property
    def cos(self):
        return math.cos(math.radians(self.roll))

    @property
    def hypot(self):
        return math.hypot(self.slope, self.height)


class CrossSectionBuilder(abc.ABC):
    @abc.abstractmethod
    def build_cross_section(self, profile, x_offset):
        pass

    @abc.abstractmethod
    def build_uv(self, profile, map_length, tex_ratio):
        pass


class CrossSectionBuilderNormal(CrossSectionBuilder):
    def __init__(self):
        self.cs = CrossSection()

    def build_cross_section(self, profile, x_offset):
        self.cs.vertices = [
            TrapezoidVertex(
                [x_offset, -profile.outer_span, -profile.height],
                [0, 0]
            ),
            TrapezoidVertex(
                [x_offset, -(profile.mid_span * profile.cos), -profile.mid_span * profile.sin],
                [0, 0]
            ),
            TrapezoidVertex(
                [x_offset, 0, 0.01],
                [0, 0]
            ),
            TrapezoidVertex(
                [x_offset, profile.mid_span * profile.cos, profile.mid_span * profile.sin],
                [0, 0]
            ),
            TrapezoidVertex(
                [x_offset, profile.outer_span, -profile.height],
                [0, 0]
            ),
        ]

    def build_uv(self, profile, x_offset, map_length, tex_ratio):
        use_legacy_mapping = (map_length == 4)

        if use_legacy_mapping:
            uv_list = [
                [0, 0],
                [0.33, 0],
                [0.5, 0],
                [0.67, 0],
                [0.1, 0]
            ]
        else:
            map_length_y = tex_ratio * map_length
            v = x_offset / map_length_y
            u_med = (profile.htw + profile.side) / map_length_y if map_length_y > 0 else 0.25
            u_outer = (profile.htw + profile.side + profile.hypot) / map_length_y if map_length_y > 0 else 0.5

            uv_list = [
                [0.5 - u_outer, v],
                [0.5 - u_med, v],
                [0.5, v],
                [0.5 + u_med, v],
                [0.5 + u_outer, v]
            ]

        for vertex, uv in zip(self.cs.vertices, uv_list):
            vertex.uv = uv

    def finish(self):
        return self.cs


class CrossSection:
    def __init__(self):
        self.vertices = []

    @property
    def num_verts(self):
        return len(self.vertices)

    def interpolate(self, other, x):
        new_cs = CrossSection()
        for self_vertex, other_vertex in zip(self.vertices, other.vertices):
            new_vertex = TrapezoidVertex(
                self_vertex.location.lerp(other_vertex.location, x),
                self_vertex.uv.lerp(other_vertex.uv, x)
            )
            new_cs.vertices.append(new_vertex)

        return new_cs


class TrapezoidVertex:
    def __init__(self, location, uv):
        self._location = mathutils.Vector(location)
        self._uv = mathutils.Vector(uv)

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, location):
        self._location = mathutils.Vector(location)

    @property
    def uv(self):
        return self._uv

    @uv.setter
    def uv(self, uv):
        self._uv = mathutils.Vector(uv)



class MeshMaker:
    # TODO: Make it possible to extrude along the bezier - it will be needed for crossings and switches
    def __init__(self, target_mesh, length, fidelity=4):
        self._bm = bmesh.new()
        self._target_mesh = target_mesh
        self._uv_layer = self._bm.loops.layers.uv.new()

        self._length = length
        self._fidelity = 4
        self._segment_length = 2 / fidelity
        self._step = length / self._segment_length
        self._num_cross_sections = math.ceil(length / self._segment_length) + 1

    def clear_mesh(self):
        self._bm.clear()

    def extrude_between(self, cs1, cs2, material_index=0):
        extrusion = []

        for cs_i in range(self._num_cross_sections):
            offset = cs_i * self._segment_length
            t = offset / self._length
            # Pseudo clamp xD
            if t > 1:
                t = 1
            cs = cs1.interpolate(cs2, t)
            extrusion.append(cs)

        # TODO: Manipulate UV to fix proportional mapping

        self._make_geometry(extrusion, material_index)

    def _make_geometry(self, cross_sections, material_index=0):
        bm_verts = []
        uvs = []

        for cs in cross_sections:
            for cs_vert in cs.vertices:
                bm_verts.append(self._bm.verts.new(cs_vert.location))
                uvs.append(cs_vert.uv)

        cs_size = cross_sections[0].num_verts
        num_faces = cs_size - 1

        for cs_idx in range(self._num_cross_sections - 1):
            for face_idx in range(num_faces):
                face_uvs = []
                face_bmverts = []

                vert_indices = [
                    0 + face_idx + cs_size * cs_idx,
                    cs_size + face_idx + cs_size * cs_idx,
                    cs_size + face_idx + cs_size * cs_idx + 1,
                    1 + face_idx + cs_size * cs_idx
                ]

                for idx in vert_indices:
                    face_bmverts.append(bm_verts[idx])
                    face_uvs.append(uvs[idx])

                bm_face = self._bm.faces.new(face_bmverts)
                bm_face.material_index = material_index

                for vertex_index, loop in enumerate(bm_face.loops):
                    loop[self._uv_layer].uv = face_uvs[vertex_index]

    def finish(self):
        self._bm.to_mesh(self._target_mesh)
        self._bm.free()
        return self._target_mesh

