import pathlib

import eu07_tools

import bpy

from common.geometry_builder import GeometryBuilder
from material_tools.input import MaterialImporter


class INCImporter:
    def __init__(self, asset_searcher):
        self.asset_searcher = asset_searcher
        self.join_into_one = False
        self.parameters = []

    def import_from_filepath(self, filepath):
        original_basedir = self.asset_searcher.basedir
        self.asset_searcher.basedir = pathlib.Path(filepath).parent

        with open(filepath, "r", encoding="latin-1") as file:
            imported = self.import_from_file(file)

        self.asset_searcher.basedir = original_basedir

        return imported

    def import_from_file(self, file):
        print(self.parameters)
        tokenizer = eu07_tools.utils.Tokenizer(parameters=self.parameters)
        elements = eu07_tools.scn.load(file, tokenizer)
        return self.import_from_elements(elements)

    def import_from_elements(self, elements):
        for element in elements:
            if element.type == "node:triangles":
                self.import_from_node_triangles_element(element)
            elif element.type == "node:model":
                self.import_from_node_model_element(element)

    def import_from_node_triangles_element(self, element):
        mesh_data = bpy.data.meshes.new(element.name)
        mesh_data = GeometryBuilder().build_from_geometry(element.geometry, mesh_data=mesh_data, swizzle=True)

        tri_object = bpy.data.objects.new(element.name, mesh_data)
        tri_object.active_material = MaterialImporter(self.asset_searcher).import_from_relpath(element.map)
        bpy.context.scene.collection.objects.link(tri_object)

        return tri_object

    def import_from_node_model_element(self, element):
        print("import nmodel")
