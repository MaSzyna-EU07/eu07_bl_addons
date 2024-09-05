import bmesh
import bpy

from eu07_tools.utils.geometry import VertexStorageSectored

# TODO: Optimize...
class GeometryBuilder:
    def __init__(self):
        pass

    def build_from_geometry(self, eu07_geometry, mesh_data=None, calc_normals=False, swizzle=False):
        bm = bmesh.new()
        uv_layer = bm.loops.layers.uv.new()

        eu07_geometry.to_triangles()

        if calc_normals:
            try:
                eu07_geometry.calc_smooth_groups_normals()
            except ValueError:
                pass

        unique_vertices = VertexStorageSectored()

        indices = []
        per_face_vertex_normals = []
        per_face_uvs = []

        for triangle in eu07_geometry.triangles:
            for vertex in triangle.vertices:

                try:
                    index = unique_vertices.find(vertex)
                except KeyError:
                    index = unique_vertices.push(vertex)
                finally:
                    indices.append(index)

                per_face_vertex_normals.append(vertex.normal)
                per_face_uvs.append(vertex.mapping)

        for vertex in unique_vertices:
            loc = vertex.location.swizzled() if swizzle else vertex.location
            bm.verts.new(loc)

        bm.verts.ensure_lookup_table()

        num_triangles = len(eu07_geometry.triangles)

        custom_normals = []

        for i in range(num_triangles):
            bm_verts = []

            for index in indices[i*3:i*3+3]:
                bm_verts.append(bm.verts[index])

            try:
                bm_face = bm.faces.new(bm_verts)
                for normal in per_face_vertex_normals[i * 3: i * 3 + 3]:
                    custom_normals.append(normal)
            except ValueError:
                pass
            else:
                for vertex_index, loop in enumerate(bm_face.loops):
                    loop[uv_layer].uv = per_face_uvs[i * 3 + vertex_index]

        if not mesh_data:
            mesh_data = bpy.data.meshes.new()

        bm.to_mesh(mesh_data)
        bm.free()

        mesh_data.normals_split_custom_set(custom_normals)

        return mesh_data