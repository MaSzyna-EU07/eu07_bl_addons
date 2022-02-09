import pathlib

import eu07_tools

from common import includes
from t3d.input import input_builders
from .geometry import Geometry


class T3DImporter:
    def __init__(self, asset_searcher):
        self.load_included_objects = True
        self.import_meshes = True
        self.import_spots = True
        self.import_stars = True
        self.asset_searcher = asset_searcher
        self.include_identifier = includes.MASTER_IDENTIFIER

    def import_from_filepath(self, filepath):
        with open(filepath, "r", encoding="latin-1") as file:
            return self.import_from_file(file)

    def import_from_file(self, file):
        elements = eu07_tools.t3d.load(file)
        return self.import_from_elements(elements)

    def import_from_elements(self, elements):
        objects = []

        for element in elements:
            if element.element_type == "submodel":
                obj = self.import_from_submodel_element(element)

                if obj:
                    objects.append(obj)

            elif element.element_type == "include":
                included_objects = self.import_from_include_element(element)
                objects.extend(included_objects)

        return objects

    def import_from_submodel_element(self, element):
        if (
                (element.type == "Mesh" and not self.import_meshes) or
                (element.type == "FreeSpotLight" and not self.import_spots) or
                (element.type == "Stars" and not self.import_stars)
        ):
            return None

        builder = input_builders.get_builder(element)

        builder.create_submodel(element.name)
        builder.set_parent(element.parent_name)
        builder.set_anim(element.anim)
        builder.set_diffuse(element.diffuse_color)
        builder.set_selfillum(element.selfillum)
        builder.set_max_distance(element.max_distance)
        builder.set_min_distance(element.min_distance)
        builder.set_transform(element.transform)

        if element.type == 'Mesh':
            builder.set_ambient(element.ambient_color)
            builder.set_specular(element.specular_color)
            builder.set_wire(element.wire)
            builder.set_wire_size(element.wire_size)
            builder.set_opacity(element.opacity)
            builder.set_map(element.map, self.asset_searcher, element.opacity)

            if element.use_indices:
                geometry = Geometry.from_indexed_t3d(
                    element.vertices, element.num_verts,
                    element.indices, element.num_indices
                )
            else:
                geometry = Geometry.from_legacy_t3d(element.triangles)

            builder.set_geometry(geometry)

        elif element.type == 'FreeSpotLight':
            builder.set_near_atten_start(element.near_atten_start)
            builder.set_near_atten_end(element.near_atten_end)
            builder.set_use_near_atten(element.use_near_atten)
            builder.set_far_atten_decay_type(element.far_atten_decay_type)
            builder.set_far_decay_radius(element.far_decay_radius)
            builder.set_falloff_angle(element.falloff_angle)
            builder.set_hotspot_angle(element.hotspot_angle)

        elif element.type == 'Stars':
            builder.set_geometry(element.stars)

        obj = builder.obj
        obj.eu07_include_identifier = self.include_identifier
        return obj

    def import_from_include_element(self, element):
        inc_path = self.asset_searcher.models.find(element.path)
        if inc_path:
            include = includes.add_include()

            full_path = pathlib.Path(inc_path)
            include.file_path = str(full_path.relative_to(self.asset_searcher.root))
            include.name = str(pathlib.Path(include.file_path).with_suffix("").stem)

            prev_inc_identifier = self.include_identifier
            self.include_identifier = include.identifier

            objects = self.import_from_filepath(inc_path) if self.load_included_objects else []

            self.include_identifier = prev_inc_identifier

            return objects

        return []
