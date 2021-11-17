import abc
import math

import bmesh
import bpy

from material_tools.input import MATImporter
from material_tools.utils import get_qualified_material_name


def get_builder(type_):
    if type_ == 'Mesh':
        cls = MeshInputBuilder
    elif type_ == 'FreeSpotLight':
        cls = FreeSpotLightInputBuilder
    elif type_ == 'Stars':
        cls = StarsInputBuilder
    else:
        raise ValueError('Unrecognized submodel type: {0}'.format(type_))

    return cls()


class SubmodelInputBuilder(abc.ABC):
    def create_submodel(self, name):
        self.obj = None

    def set_parent(self, parent_name):
        self.obj.parent = bpy.data.objects.get(parent_name)

    def set_diffuse(self, diffuse):
        self.obj.t3d_properties.diffuse_color = diffuse / 255.0

    def set_selfillum(self, selfillum):
        self.obj.t3d_properties.selfillum = selfillum

    def set_anim(self, anim):
        self.obj.t3d_properties.anim = anim

    def set_max_distance(self, max_distance):
        self.obj.t3d_properties.max_distance = max_distance

    def set_min_distance(self, min_distance):
        self.obj.t3d_properties.min_distance = min_distance

    def set_transform(self, transform):
        self.obj.matrix_basis = [
            transform[:4],
            transform[4:8],
            transform[8:12],
            transform[12:]
        ]

class MeshInputBuilder(SubmodelInputBuilder):
    def create_submodel(self, name: str):
        mesh = bpy.data.meshes.new(name)
        self.obj = bpy.data.objects.new(name, mesh)

    def set_ambient(self, ambient_color):
        self.obj.t3d_properties.ambient_color = ambient_color / 255.0

    def set_specular(self, specular_color):
        self.obj.t3d_properties.specular_color = specular_color / 255.0

    def set_wire(self, wire):
        self.obj.t3d_properties.wire = wire

    def set_wire_size(self, wire_size):
        self.obj.t3d_properties.wire_size = wire_size

    def set_opacity(self, opacity):
        self.obj.t3d_properties.opacity = opacity

    def set_map(self, map_, asset_searcher):
        if map_ == "none":
            return

        is_repl = map_ in ["-1", "-2", "-3", "-4", "replacableskin"]

        if is_repl:
            if map_ == "replacableskin":
                map_ = "-1"

            self.obj.t3d_properties.replacableskin_id = map_

            repl_mat_name = f"Replacableskin {map_}"
            self.obj.active_material = bpy.data.materials.get(
                repl_mat_name,
                bpy.data.materials.new(repl_mat_name)
            )

        else:
            abspath = asset_searcher.textures.find(map_)

            material = bpy.data.materials.get(get_qualified_material_name(abspath))

            if not material:
                material = MATImporter(asset_searcher).import_from_abspath(abspath)

            self.obj.active_material = material

    def set_geometry(self, submodel):
        bm = bmesh.new()
        uv_layer = bm.loops.layers.uv.new()
        custom_normals = []

        if submodel.use_indices:
            self.obj.t3d_properties.use_face_indices = True

            for vertex in submodel.vertices:
                bm_vertex = bm.verts.new(vertex.location)
                custom_normals.append(vertex.normal)

            bm.verts.ensure_lookup_table()

            num_triangles = submodel.num_indices // 3

            for i in range(num_triangles):
                bm_verts = []
                uvs = []

                for index in submodel.indices[i*3:i*3+3]:
                    bm_verts.append(bm.verts[index])

                    vertex = submodel.vertices[index]
                    uvs.append(vertex.mapping)

                bm_face = bm.faces.new(bm_verts)

                for vertex_index, loop in enumerate(bm_face.loops):
                    loop[uv_layer].uv = uvs[vertex_index]

        else:
            for triangle in submodel.triangles:
                bm_vertices = []

                for vertex in triangle.vertices:
                    bm_vertex = bm.verts.new(vertex.location)

                    if vertex.use_normal:
                        custom_normals.append(vertex.normal)
                        self.obj.t3d_properties.use_normals = True

                    bm_vertices.append(bm_vertex)

                bm.verts.ensure_lookup_table()

                bm_face = bm.faces.new(bm_vertices)
                bm_face.smooth = (triangle.smooth > 0)

                for vertex_index, loop in enumerate(bm_face.loops):
                    loop[uv_layer].uv = triangle.vertices[vertex_index].mapping

            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.00001)

        bm.to_mesh(self.obj.data)
        bm.free()

        if custom_normals:
            self.obj.data.use_auto_smooth = True
            self.obj.data.normals_split_custom_set_from_vertices(custom_normals)


class FreeSpotLightInputBuilder(SubmodelInputBuilder):
    def create_submodel(self, name: str):
        data = bpy.data.lights.new(name, type='SPOT')
        self.obj = bpy.data.objects.new(name, data)

    def set_diffuse(self, diffuse):
        self.obj.data.color = [value / 255 for value in diffuse]

    def set_selfillum(self, selfillum):
        self.obj.t3d_properties.selfillum_spot = selfillum

    def set_near_atten_start(self, near_atten_start):
        self.obj.t3d_properties.near_atten_start = near_atten_start

    def set_near_atten_end(self, near_atten_end):
        self.obj.t3d_properties.near_atten_end = near_atten_end

    def set_use_near_atten(self, use_near_atten):
        self.obj.t3d_properties.use_near_atten = use_near_atten

    def set_far_atten_decay_type(self, far_atten_decay_type):
        self.obj.t3d_properties.far_atten_decay_type = far_atten_decay_type

    def set_far_decay_radius(self, far_decay_radius):
        self.obj.data.distance = far_decay_radius

    def set_falloff_angle(self, falloff_angle):
        pass  # TODO: Nice way to set spot_blend

    def set_hotspot_angle(self, hotspot_angle):
        self.obj.data.spot_size = math.radians(hotspot_angle)


class StarsInputBuilder(SubmodelInputBuilder):
    def create_submodel(self, name: str):
        self.obj = bpy.data.objects.new(name, None)

    def set_geometry(self, geometry):
        for star in geometry:
                point = bpy.data.lights.new(
                    f"{self.obj.name}.star",
                    'POINT'
                )
                star_obj = bpy.data.objects.new(point.name, point)
                star_obj.parent = self.obj
                bpy.context.scene.collection.objects.link(star_obj)

                star_obj.location = star.location
                star_obj.data.color = [a / 255 for a in star.rgb_color]
