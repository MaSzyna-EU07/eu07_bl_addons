import abc
import math
import mathutils
import collections
from ... import eu07_tools

import bmesh
import bpy

from ...common.geometry_builder import GeometryBuilder
from ...material_tools.input import MaterialImporter
from ...material_tools.utils import get_qualified_material_name
from .. import sim_light


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

    def set_parent_name(self, parent_name):
        if parent_name == "none":
            return

        self.obj.parent = bpy.data.objects.get(parent_name)

    def set_diffuse_color(self, diffuse):
        self.obj.t3d_properties.diffuse_color = diffuse / 255.0

    def set_selfillum(self, selfillum):
        self.obj.t3d_properties.selfillum = selfillum

    def set_anim(self, anim):
        self.obj.t3d_properties.anim = anim

    def set_max_distance(self, max_distance):
        self.obj.t3d_properties.max_distance = max_distance

    def set_min_distance(self, min_distance):
        self.obj.t3d_properties.min_distance = min_distance

    def set_transform(self, transform, initialrotate_matrix=None):
        self.obj.matrix_basis = [
            transform[:4],
            transform[4:8],
            transform[8:12],
            transform[12:]
        ]

        if initialrotate_matrix is not None and self.obj.parent is None:
            self.obj.matrix_basis = initialrotate_matrix @ self.obj.matrix_basis

class MeshInputBuilder(SubmodelInputBuilder):
    def create_submodel(self, name: str):
        mesh = bpy.data.meshes.new(name)
        self.obj = bpy.data.objects.new(name, mesh)

    def set_ambient_color(self, ambient_color):
        self.obj.t3d_properties.ambient_color = ambient_color / 255.0

    def set_specular_color(self, specular_color):
        self.obj.t3d_properties.specular_color = specular_color / 255.0

    def set_wire(self, wire):
        self.obj.t3d_properties.wire = wire

    def set_wire_size(self, wire_size):
        self.obj.t3d_properties.wire_size = wire_size

    def set_opacity(self, opacity):
        self.obj.t3d_properties.opacity = opacity

    def set_map(self, map_, asset_searcher, opacity, diffuse):
        if map_ == "none":
            return

        if map_.is_skin:
            self.obj.t3d_properties.replacableskin_id = str(map_.skin_index)

            repl_mat_name = f"replacableskin({map_})"
            if repl_mat_name in bpy.data.materials:
                self.obj.active_material = bpy.data.materials[repl_mat_name]
            else:
                self.obj.active_material = bpy.data.materials.new(repl_mat_name)

        else:
            abspath = asset_searcher.textures.find(map_.resource_path)
            self.obj.t3d_properties.opacity_source = "OBJECT"

            if abspath:
                material = bpy.data.materials.get(get_qualified_material_name(abspath))

                if not material:
                    material = MaterialImporter(asset_searcher).import_from_abspath(abspath, traits=map_.get_traits_str())
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
        self._cos_falloff = 0.0
        sim_light.make_simulator_light(data)

    def set_diffuse_color(self, diffuse):
        self.obj.data.color = sim_light.diffuse_to_color(diffuse)

    def set_hotspot_power(self, hotspot_power):
        # the simulator takes 100 for a missing or a non-positive one
        if hotspot_power is None or hotspot_power <= 0:
            hotspot_power = 100.0
        self.obj.data.energy = sim_light.power_to_energy(hotspot_power)

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
        self.obj.t3d_properties.far_decay_radius = far_decay_radius

    def set_falloff_angle(self, falloff_angle):
        self._cos_falloff = sim_light.angle_to_cos(falloff_angle)
        sim_light.set_cones(self.obj.data, self._cos_falloff, self._cos_falloff)

    # NOTE: This should be called only after set_falloff_angle
    def set_hotspot_angle(self, hotspot_angle):
        sim_light.set_cones(self.obj.data, self._cos_falloff, sim_light.angle_to_cos(hotspot_angle))

class StarsInputBuilder(SubmodelInputBuilder):
    def create_submodel(self, name: str):
        self.obj = bpy.data.objects.new(name, None)

    def set_points(self, geometry):
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
