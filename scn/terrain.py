import eu07_tools
import bpy
import bmesh

from common import get_path_from_material
from mat.input import MATImporter

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
            material = MATImporter.import_from_relpath(map_)

            self._terrain_object.data.materials.append(material)

        return self._terrain_object


def create_node_triangles_from_mesh(terrain_object):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = terrain_object.evaluated_get(depsgraph)

    mesh = bpy.data.meshes.new_from_object(obj_eval)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    uv_layer = mesh.uv_layers.active
    if uv_layer:
        uv_data = uv_layer.data[:]

    mesh.validate_material_indices()
    mesh.calc_normals_split()
    for polygon in mesh.polygons:
        node = eu07_tools.scn.create_element("node:triangles")

        material = mesh.materials[polygon.material_index]
        node.map = get_path_from_material(material)

        for loop_index in polygon.loop_indices:
            loop = mesh.loops[loop_index]

            xyz = eu07_tools.utils.swizzle_coords(terrain_object.matrix_world @ mesh.vertices[loop.vertex_index].co)
            ijk = eu07_tools.utils.swizzle_coords(loop.normal)
            uv = uv_data[loop_index].uv if uv_layer else [0, 0]

            node.vertices.new((*xyz, *ijk, *uv))
        yield node

    bpy.data.meshes.remove(mesh)