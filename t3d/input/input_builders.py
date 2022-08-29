import abc
import math
import mathutils
import collections
import eu07_tools

import bmesh
import bpy

from common.geometry_builder import GeometryBuilder
from material_tools.input import MaterialImporter
from material_tools.utils import get_qualified_material_name


def get_builder(element, banan_as_mesh=False):
    if element is None:
        return None

    if element.type == 'Mesh':
        cls = MeshInputBuilder
        if element.geometry.is_empty and not banan_as_mesh:
            cls = BananMeshInputBuilder
    elif element.type == 'FreeSpotLight':
        cls = FreeSpotLightInputBuilder
    elif element.type == 'Stars':
        cls = StarsInputBuilder
    else:
        raise ValueError('Unrecognized submodel type: {0}'.format(element.type_))

    return cls()


class SubmodelInputBuilder(abc.ABC):
    def create_submodel(self, name):
        self.obj = None

    def set_parent(self, parent_name):
        if parent_name == "none":
            return

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

    def set_map(self, map_, asset_searcher, opacity, diffuse):
        if map_ == "none":
            # name = f"Color {' '.join((str(int(x)) for x in diffuse))}"
            #
            # try:
            #     self.obj.active_material = bpy.data.materials[name]
            # except KeyError:
            #     material = self.obj.active_material = bpy.data.materials.new(name)
            #     wrapper = MaterialWrapper(material)
            #     wrapper.initialize()
            #     wrapper.set_diffuse_color(diffuse / 255)

            return

        is_repl = map_ in ["-1", "-2", "-3", "-4", "replacableskin"]

        if is_repl:
            if map_ == "replacableskin":
                map_ = "-1"

            self.obj.t3d_properties.replacableskin_id = map_

            repl_mat_name = f"replacableskin({map_})"
            if repl_mat_name in bpy.data.materials:
                self.obj.active_material = bpy.data.materials[repl_mat_name]
            else:
                self.obj.active_material = bpy.data.materials.new(repl_mat_name)
                self.obj.active_material.use_nodes = True

        else:
            abspath = asset_searcher.textures.find(map_)
            self.obj.t3d_properties.opacity_source = "OBJECT"

            if abspath:
                material = bpy.data.materials.get(get_qualified_material_name(abspath))

                if not material:
                    material = MaterialImporter(asset_searcher).import_from_abspath(abspath, opacity=opacity)
                    self.obj.t3d_properties.opacity_source = "MATERIAL"

                self.obj.active_material = material

    def set_geometry(self, geometry):
        geo_builder = GeometryBuilder()
        mesh_data = geo_builder.build_from_geometry(geometry, self.obj.data, calc_normals=True)
        self.obj.data = mesh_data


class BananMeshInputBuilder(MeshInputBuilder):
    def create_submodel(self, name):
        self.obj = bpy.data.objects.new(name, None)

    def set_map(self, map_, asset_searcher, opacity, diffuse):
        pass

    def set_geometry(self, geometry):
        pass

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
        if self._is_cosinus(falloff_angle):
            self.obj.data.spot_size = math.acos(falloff_angle) * 2
        else:
            self.obj.data.spot_size = math.radians(falloff_angle)

    # NOTE: This should be called only after set_falloff_angle
    def set_hotspot_angle(self, hotspot_angle):
        if self._is_cosinus(hotspot_angle):
            hotspot_angle = math.acos(hotspot_angle) * 2
            falloff_angle = self.obj.data.spot_size
        else:
            falloff_angle = math.degrees(self.obj.data.spot_size)

        self.obj.data.spot_blend = 1 - hotspot_angle / falloff_angle

    def _is_cosinus(self, spot_angle):
        return spot_angle <= 1

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
