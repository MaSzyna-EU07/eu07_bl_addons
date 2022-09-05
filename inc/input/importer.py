import pathlib

import eu07_tools

import bpy
import mathutils

from common.geometry_builder import GeometryBuilder
from material_tools.input import MaterialImporter

from e3d.input import E3DImporter
from t3d.input import T3DImporter
from t3d.utils import join_meshes_into_one


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
        objects = []

        for element in elements:
            obj = None

            if element.type == "node:triangles":
                obj = self.import_from_node_triangles_element(element)
            elif element.type == "node:model":
                obj = self.import_from_node_model_element(element)

            if obj:
                objects.append(obj)
                bpy.context.scene.collection.objects.link(obj)

        merged = join_meshes_into_one(objects)


    def import_from_node_triangles_element(self, element):
        mesh_data = bpy.data.meshes.new(element.name)
        mesh_data = GeometryBuilder().build_from_geometry(element.geometry, mesh_data=mesh_data, swizzle=True)

        tri_object = bpy.data.objects.new(element.name, mesh_data)
        tri_object.active_material = MaterialImporter(self.asset_searcher).import_from_relpath(element.map)

        return tri_object

    def import_from_node_model_element(self, element):
        fullpath = self.asset_searcher.models.find(element.path)

        importer = None
        if fullpath.endswith(".e3d"):
            importer = E3DImporter(self.asset_searcher)
            importer.import_stars = False
            importer.import_spots = False
            importer.join_into_one = True
            importer.import_lod = False

        elif fullpath.endswith(".t3d"):
            importer = T3DImporter(self.asset_searcher)
            importer.load_included_objects = True
            importer.import_stars = False
            importer.import_spots = False
            importer.join_into_one = True
            importer.import_lod = False
        else:
            pass

        if importer is None:
            return

        objects = importer.import_from_filepath(fullpath)

        for obj in objects:
            obj.location += mathutils.Vector(element.location.swizzled())

            return obj