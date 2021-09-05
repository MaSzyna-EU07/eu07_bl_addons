import eu07_tools
import bpy
import bmesh

from ..mat import HelperMATImporter

class TerrainBuilder:
    def __init__(self, config):
        self._config = config
        self._terrain_mesh = bmesh.new()
        self._uv_layer = self._terrain_mesh.loops.layers.uv.new()
        self._terrain_object = bpy.data.objects.new("terrain", bpy.data.meshes.new("terrain"))
        self._terrain_object.scn_properties.type_ = "node:triangles"
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
                bm_vert = self._terrain_mesh.verts.new(eu07_tools.utils.swizzle_coords(vertex.location))
                bm_face_verts.append(bm_vert)

            bm_face = self._terrain_mesh.faces.new(bm_face_verts)
            bm_face.material_index = material_index

            for vertex_index, loop in enumerate(bm_face.loops):
                loop[self._uv_layer].uv = vertices[vertex_index].mapping

    def finish(self):
        if self._config.get("do_weld_terrain"):
            bmesh.ops.remove_doubles(self._terrain_mesh, verts=self._terrain_mesh.verts, dist=0.00001)
        self._terrain_mesh.to_mesh(self._terrain_object.data)
        self._terrain_mesh.free()


        for map_ in self._maps:
            map_ = map_.split(":")[0]
            material = HelperMATImporter.import_material_from_relpath(map_)

            self._terrain_object.data.materials.append(material)