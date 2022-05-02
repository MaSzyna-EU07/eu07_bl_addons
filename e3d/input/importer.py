import math

import bpy
import eu07_tools

from t3d.input import input_builders

import mathutils


class E3DImporter:
    def __init__(self, asset_searcher):
        self.import_meshes = True
        self.import_spots = True
        self.import_stars = True
        self.asset_searcher = asset_searcher

    def import_from_filepath(self, filepath):
        with open(filepath, "rb") as file:
            return self.import_from_file(file)

    def import_from_file(self, file):
        model = eu07_tools.e3d.load(file)
        return self.import_from_model(model)

    def import_from_model(self, model):
        objects = []

        for submodel in model.submodels:
            obj = self.import_from_submodel_element(submodel)

            if obj:
                objects.append(obj)

        return objects

    def import_from_submodel_element(self, submodel):
        if (
                (submodel.type == "Mesh" and not self.import_meshes) or
                (submodel.type == "FreeSpotLight" and not self.import_spots) or
                (submodel.type == "Stars" and not self.import_stars)
        ):
            return None

        builder = input_builders.get_builder(submodel)

        builder.create_submodel(submodel.name)
        builder.set_parent(submodel.parent_name)
        builder.set_anim(submodel.anim)
        # All colors are multiplied, because in E3D they are in range 0-1, while in T3D in range 0-255
        builder.set_diffuse(submodel.diffuse_color[:3] * 255)
        builder.set_selfillum(submodel.selfillum)
        builder.set_max_distance(submodel.max_distance)
        builder.set_min_distance(submodel.min_distance)
        builder.set_transform(submodel.transform)

        if submodel.type == 'Mesh':
            builder.set_ambient(submodel.ambient_color[:3] * 255)
            builder.set_specular(submodel.specular_color[:3] * 255)
            builder.set_wire_size(submodel.wire_size)

            opacity = 1
            if submodel.flags & (1 << 5):
                opacity = 0

            builder.set_map(submodel.map, self.asset_searcher, opacity, submodel.diffuse_color[:3] * 255)

            geometry = Geometry.from_e3d(submodel.get_triangles_iter())
            # Because weird rotations are made by EU07.exe during e3d generation,
            # we need to compensate them
            matrix = mathutils.Matrix.Rotation(math.radians(90), 4, 'X')
            builder.set_geometry(geometry)

        elif submodel.type == 'FreeSpotLight':
            builder.set_near_atten_start(submodel.near_atten_start)
            builder.set_near_atten_end(submodel.near_atten_end)
            builder.set_use_near_atten(submodel.use_near_atten)
            builder.set_far_atten_decay_type(submodel.far_atten_decay_type)
            builder.set_far_decay_radius(submodel.far_decay_radius)
            builder.set_falloff_angle(submodel.cos_falloff_angle)
            builder.set_hotspot_angle(submodel.cos_hotspot_angle)

        elif submodel.type == 'Stars':
            builder.set_geometry(submodel.stars)

        return builder.obj

    def _set_geometry(self):
        pass