import bpy
import bmesh

# This is spaghetti, written for experimental purposes - needs to be refactored


class SceneryBuilder:
    def __init__(self):
        self._terrain_builder = _TerrainBuilder()

    def run(self, data):
        for element in data:
            if element.typename == "node:triangles":
                self._terrain_builder.add_triangle(element)
                

        self._terrain_builder.finish()


class _TerrainBuilder:
    def __init__(self):
        self._terrain_mesh = bmesh.new()
        self._terrain_object = bpy.data.objects.new("terrain", bpy.data.meshes.new("terrain"))
        bpy.context.scene.collection.objects.link(self._terrain_object)

        self._materials_buffer = [

        ]

    def add_triangle(self, element):


        num_triangles = len(element.vertices) // 3

        for triangle_idx in range(num_triangles):
            vertices = element.vertices[
                triangle_idx * 3 : triangle_idx * 3 + 3
            ]

            bm_face_verts = []
            for vertex in vertices:
                bm_vert = self._terrain_mesh.verts.new(
                    (-vertex.location.x, vertex.location.z, vertex.location.y)
                )
                bm_face_verts.append(bm_vert)

            bm_face = self._terrain_mesh.faces.new(bm_face_verts)

    def finish(self):
        # remove doubles?
        self._terrain_mesh.to_mesh(self._terrain_object.data)
        self._terrain_mesh.free()
            