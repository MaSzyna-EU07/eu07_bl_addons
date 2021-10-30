import pathlib

import bpy
import eu07_tools

from common.utils import get_root
from common import includes
from t3d.input import input_builders


# TODO: Move to utils
def merge_objects_to_master(objects, master):
    bpy.ops.object.select_all(action='DESELECT')

    master.select_set(True)
    bpy.context.view_layer.objects.active = master

    for obj in objects:
        obj.select_set(True)

    bpy.ops.object.join()


class T3DImporter:
    def __init__(self):
        self.load_includes = True
        self.import_meshes = True
        self.import_spots = True
        self.import_stars = True
        self.merge_to_single_mesh = False
        self.asset_searcher = eu07_tools.utils.AssetSearcher(get_root())
        self.include_identifier = includes.MASTER_IDENTIFIER

    def import_from_filepath(self, filepath):
        with open(self.filepath, "r", encoding="latin-1") as file:
            return self.import_from_file(file)

    def import_from_file(self, file):
        elements = eu07_tools.t3d.load(file)
        return self.import_elements(elements)

    def import_from_elements(self, elements):
        objects = []

        for element in elements:
            if element.element_type == "submodel":
                obj = self.import_from_submodel_element(element)
                objects.append(obj)

            elif element.element_type == "include" and self.load_includes:
                included_objects = self.import_from_include_element(element)
                objects.extend(included_objects)

        return objects

    def import_from_include_element(self, element):
        inc_path = self.asset_searcher.models.find(element.path)
        if inc_path:
            include = includes.add_include()

            full_path = pathlib.Path(inc_path)
            include.file_path = str(full_path.relative_to(self.asset_searcher.root))
            include.name = str(pathlib.Path(include.file_path).with_suffix("").stem)

            self.include_identifier = include.identifier
            objects = self.import_from_filepath(inc_path)
            self.include_identifier = includes.MASTER_IDENTIFIER

            return objects

        return []

    def import_from_submodel_element(self, element):
        builder = input_builders.get_builder(element.type)

        builder.create_element(element.name)
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
            builder.set_map(element.map, self.asset_searcher)
            builder.set_geometry(element)

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

        return builder.obj

