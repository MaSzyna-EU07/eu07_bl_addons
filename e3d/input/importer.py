import math
import pathlib

import bpy
from ... import eu07_tools

from ...t3d.input import input_builders

import mathutils

from ...t3d.utils import join_meshes_into_one


class E3DImporter:
    def __init__(self, asset_searcher):
        self.import_meshes = True
        self.import_spots = True
        self.import_stars = True
        self.asset_searcher = asset_searcher
        self.join_into_one = False
        self.import_lod = True
        self.name_prefix = ""
        # lights of the model which its objects don't shadow, see input_builders.shade_self_pending()
        self._unshaded_lights = []

    def import_from_filepath(self, filepath):
        original_basedir = self.asset_searcher.basedir
        self.asset_searcher.basedir = pathlib.Path(filepath).parent

        with open(filepath, "rb") as file:
            return self.import_from_file(file)

        self.asset_searcher.basedir = original_basedir

        return imported

    def import_from_file(self, file):
        model = eu07_tools.e3d.load(file)
        return self.import_from_model(model)

    def import_from_model(self, model):
        objects = []
        self._unshaded_lights = []

        if self.join_into_one:
            self.import_spots = False
            self.import_stars = False
            self.import_lod = False

        for submodel in model.submodels:
            if not self.import_lod and submodel.min_distance > 0:
                continue

            obj = self.import_from_submodel_element(submodel)

            if obj:
                objects.append(obj)

        if self.join_into_one and objects:
            combined = join_meshes_into_one(objects)

            return [combined]

        input_builders.shade_self_pending(self._unshaded_lights, objects)
        return objects

    def import_from_submodel_element(self, submodel):
        if (
                (submodel.type == "Mesh" and not self.import_meshes) or
                (submodel.type == "FreeSpotLight" and not self.import_spots) or
                (submodel.type == "Stars" and not self.import_stars)
        ):
            return None

        builder = input_builders.get_builder(submodel, self.join_into_one)

        builder.create_submodel(f"{self.name_prefix}{submodel.name}")
        builder.set_parent_name(f"{self.name_prefix}{submodel.parent_name}")
        builder.set_anim(submodel.anim)
        # All colors are multiplied, because in E3D they are in range 0-1, while in T3D in range 0-255
        builder.set_diffuse_color(submodel.diffuse_color[:3] * 255)
        builder.set_selfillum(submodel.selfillum)
        builder.set_max_distance(math.sqrt(submodel.max_distance))
        builder.set_min_distance(math.sqrt(submodel.min_distance))

        initialrotate_matrix = mathutils.Matrix((
            (-1, 0, 0, 0),
            (0, 0, 1, 0),
            (0, 1, 0, 0),
            (0, 0, 0, 1),
        ))
        builder.set_transform(submodel.transform, initialrotate_matrix)

        if submodel.type == 'Mesh':
            builder.set_ambient_color(submodel.ambient_color[:3] * 255)
            builder.set_specular_color(submodel.specular_color[:3] * 255)
            builder.set_wire_size(submodel.wire_size)

            opacity = 1
            if submodel.flags & (1 << 5):
                opacity = 0

            builder.set_map(submodel.map, self.asset_searcher, opacity, submodel.diffuse_color[:3] * 255)
            builder.set_geometry(submodel.get_geometry())

        elif submodel.type == 'FreeSpotLight':
            builder.set_near_atten_start(submodel.near_atten_start)
            builder.set_near_atten_end(submodel.near_atten_end)
            builder.set_use_near_atten(submodel.use_near_atten)
            builder.set_far_atten_decay_type(submodel.far_atten_decay_type)
            builder.set_far_decay_radius(submodel.far_decay_radius)
            builder.set_falloff_angle(submodel.cos_falloff_angle)
            builder.set_hotspot_angle(submodel.cos_hotspot_angle)
            builder.set_hotspot_power(submodel.hotspot_power * 100)
            builder.set_radius(submodel.radius)
            builder.set_cast_shadows(submodel.cast_shadows)
            builder.set_soft_falloff(submodel.soft_falloff)
            builder.set_shade_self(submodel.shade_self)
            builder.set_light_only(submodel.light_only)
            if submodel.cast_shadows and not builder.shade_self:
                self._unshaded_lights.append(builder.obj)

        elif submodel.type == 'Stars':
            builder.set_points(submodel.stars)

        return builder.obj

    def _set_geometry(self):
        pass