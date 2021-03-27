import abc
import math
import os
import warnings
from pathlib import Path

import bmesh
import bpy
import eu07_tools
from ..common import create_material_from_abspath


def import_model(elements, collection, config):
    for element in elements:

        if element.element_type == "submodel":
            obj = _build_object(element, config)
            collection.objects.link(obj)

        elif element.element_type == "include" and config.load_includes:
            full_path = config.asset_searcher.models.find(element.path)

            if Path(full_path).exists():
                inc_collection = bpy.data.collections.new(
                    f"include {' '.join([element.path, *element.parameters])} end"
                )
                collection.children.link(inc_collection)
            
                with open(full_path, "r", encoding="latin-1") as inc_file:
                    inc_elements = eu07_tools.t3d.load(inc_file)
                    import_model(inc_elements, inc_collection, config)

            else:
                config.report_func({"WARNING"}, f"Can't find included file: {element.path}")


def _build_object(submodel, config):
    builder = _get_builder(submodel.type, config)

    builder.create_submodel(submodel.name)
    builder.set_parent(submodel.parent_name)
    builder.set_anim(submodel.anim)
    builder.set_diffuse(submodel.diffuse_color)
    builder.set_selfillum(submodel.selfillum)
    builder.set_max_distance(submodel.max_distance)
    builder.set_min_distance(submodel.min_distance)
    builder.set_transform(submodel.transform)


    if submodel.type == 'Mesh':
        builder.set_ambient(submodel.ambient_color)
        builder.set_specular(submodel.specular_color)
        builder.set_wire(submodel.wire)
        builder.set_wire_size(submodel.wire_size)
        builder.set_opacity(submodel.opacity)
        builder.set_map(submodel.map)
        builder.set_geometry(submodel.triangles)

    elif submodel.type == 'FreeSpotLight':
        builder.set_near_atten_start(submodel.near_atten_start)
        builder.set_near_atten_end(submodel.near_atten_end)
        builder.set_use_near_atten(submodel.use_near_atten)
        builder.set_far_atten_decay_type(submodel.far_atten_decay_type)
        builder.set_far_decay_radius(submodel.far_decay_radius)
        builder.set_falloff_angle(submodel.falloff_angle)
        builder.set_hotspot_angle(submodel.hotspot_angle)

    elif submodel.type == 'Stars':
        builder.set_geometry(submodel.stars)

    return builder.obj
        

def _get_builder(type_, config):
    if type_ == 'Mesh':
        cls = MeshInputBuilder
    elif type_ == 'FreeSpotLight':
        cls = FreeSpotLightInputBuilder
    elif type_ == 'Stars':
        cls = StarsInputBuilder
    else:
        raise ValueError('Unrecognized submodel type: {0}'.format(type_))

    return cls(config)


class SubmodelInputBuilder(abc.ABC):
    def __init__(self, config):
        self._config = config

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
    def __init__(self, config):
        super().__init__(config)

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

    def set_map(self, map_: str):
        if map_ in ["-1", "-2", "-3", "-4", "replacableskin"]:
            full_path = self._config.skins[map_]
            if map_ == "replacableskin":
                map_ = "-1"
            self.obj.t3d_properties.replacableskin_id = map_
        elif map_ == "none":
            full_path = ""
        else:
            full_path = self._config.asset_searcher.textures.find(map_)

        if full_path:
            duplicates_allowed = self._config.allow_duplicated_materials
            self.obj.active_material = create_material_from_abspath(full_path, duplicates_allowed)

    def set_geometry(self, geometry):
        bm = bmesh.new()
        uv_layer = bm.loops.layers.uv.new()

        for triangle in geometry:
            bm_vertices = []

            for vertex in triangle.vertices:
                bm_vertex = bm.verts.new(vertex.location)
                if vertex.use_normal:
                    bm_vertex.normal = vertex.normal
                    self.obj.t3d_properties.use_normals = True

                bm_vertices.append(bm_vertex)

            bm_face = bm.faces.new(bm_vertices)
            bm_face.smooth = (triangle.smooth > 0)

            for vertex_index, loop in enumerate(bm_face.loops):
                loop[uv_layer].uv = triangle.vertices[vertex_index].mapping

        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.00001)
        bm.to_mesh(self.obj.data)
        bm.free()


class FreeSpotLightInputBuilder(SubmodelInputBuilder):
    def create_submodel(self, name: str):
        data = bpy.data.lights.new(name, type='SPOT')
        self.obj = bpy.data.objects.new(name, data)

    def set_diffuse(self, diffuse):
        self.obj.data.color = [value / 255 for value in diffuse]

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
    def __init__(self, config):
        super().__init__(config)

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
                # TODO: Link to parent's collection
                bpy.context.scene.collection.objects.link(star_obj)

                star_obj.location = star.location
                star_obj.data.color = [a / 255 for a in star.rgb_color]
