from pathlib import Path
import math

import bmesh
import mathutils
import bpy
import eu07_tools
from ..common import create_material_from_path
from .utils import get_materials_for_trajectory

from .tracks_builder import TracksBuilder

# This is spaghetti, written for experimental purposes - needs to be refactored

class SceneryBuilder:
    def __init__(self, config):
        self._terrain_builder = _TerrainBuilder(config)
        self._tracks_builder = TracksBuilder(config)
        self._lines_builder = _LinesBuilder(config)

    def run(self, data):
        for element in data:
            if element.type == "node:triangles":
                self._terrain_builder.add_triangle(element)
            elif element.type == "node:track":
                self._tracks_builder.build_trajectory(element)
            elif element.type == "node:lines":
                self._lines_builder.add_line(element)
            elif element.type == "include":
                if (element.path.endswith(".inc")):
                    pass
        self._terrain_builder.finish()
        self._lines_builder.finish()


class _LinesBuilder:
    def __init__(self, config):
        self._config = config
        self._lines_mesh = bmesh.new()
        self._lines_object = bpy.data.objects.new("lines", bpy.data.meshes.new("lines"))
        bpy.context.scene.collection.objects.link(self._lines_object)

    def add_line(self, lines_node):
        edge_verts = []

        if lines_node.subtype == "normal":
            pass

        else:
            for point in lines_node.points:
                bm_vert = self._lines_mesh.verts.new(eu07_tools.utils.switch_coordinate_system(point))
                edge_verts.append(bm_vert)

                if len(edge_verts) == 2:
                    bm_edge = self._lines_mesh.edges.new(edge_verts)
                    edge_verts.pop(0)
            
            if lines_node.subtype == "loop":
                self._lines_mesh.verts.ensure_lookup_table()
                # close da loop
                bm_edge = self._lines_mesh.edges.new((
                    self._lines_mesh.verts[0],
                    self._lines_mesh.verts[-1]
                ))

    def finish(self):
        self._lines_mesh.to_mesh(self._lines_object.data)
        self._lines_mesh.free()





class _TerrainBuilder:
    def __init__(self, config):
        self._config = config
        self._terrain_mesh = bmesh.new()
        self._uv_layer = self._terrain_mesh.loops.layers.uv.new()
        self._terrain_object = bpy.data.objects.new("terrain", bpy.data.meshes.new("terrain"))
        bpy.context.scene.collection.objects.link(self._terrain_object)

        self._maps = []

    def add_triangle(self, element):
        num_triangles = len(element.vertices) // 3


        try:
            material_index = self._maps.index(element.map)
        except ValueError:
            self._maps.append(element.map)
            material_index = len(self._maps) - 1

        for triangle_idx in range(num_triangles):
            vertices = element.vertices[
                triangle_idx * 3 : triangle_idx * 3 + 3
            ]

            bm_face_verts = []
            for vertex in vertices:
                bm_vert = self._terrain_mesh.verts.new(eu07_tools.utils.switch_coordinate_system(vertex.location))
                bm_face_verts.append(bm_vert)

            bm_face = self._terrain_mesh.faces.new(bm_face_verts)
            bm_face.material_index = material_index

            for vertex_index, loop in enumerate(bm_face.loops):
                loop[self._uv_layer].uv = vertices[vertex_index].mapping

    def finish(self):
        # remove doubles?
        self._terrain_mesh.to_mesh(self._terrain_object.data)
        self._terrain_mesh.free()


        for map_ in self._maps:
            map_ = map_.lstrip("@").split(":")[0]
            abspath = self._config["asset_searcher"].textures.find(map_)
            material = create_material_from_path(abspath, False)

            self._terrain_object.data.materials.append(material)
