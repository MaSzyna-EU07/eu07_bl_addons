import math

import mathutils

import eu07_tools


class Geometry:
    def __init__(self, vertices, num_vertices, tri_indices, num_indices):
        self.vertices = vertices
        self.num_vertices = num_vertices
        self.tri_indices = tri_indices
        self.num_indices = num_indices

    @classmethod
    def from_legacy_t3d(cls, triangles):
        geometry_data = GeometryProcessor().process_legacy_t3d(triangles)
        return cls(*geometry_data)

    @classmethod
    def from_e3d(cls, vertices_e3d):
        geometry_data = GeometryProcessor().process_e3d(vertices_e3d)
        return cls(*geometry_data)

    @classmethod
    def from_indexed_t3d(cls, vertices, num_verts, tri_indices, num_indices):
        return cls(vertices, num_verts, tri_indices, num_indices)


class GeometryProcessor:
    def process_legacy_t3d(self, triangles):
        verts_storage = VertexStorageSectored()
        num_indices = 0
        tris_indices = []

        tris_normals = self._calc_triangles_normals(triangles)

        for triangle_index, triangle in enumerate(triangles):
            for vertex in triangle.vertices:
                if not vertex.use_normal:
                    if triangle.smooth == 0:
                        vertex.normal = tris_normals[triangle_index]
                    # elif triangle.smooth > 0:
                    #     vertex.normal = self._smooth_vertex_normal(
                    #         triangle.smooth, vertex.location,
                    #         triangles, tris_normals, triangle_index
                    #     )
                    #     triangle.smooth = -1

                try:
                    vertex_index = verts_storage.find(vertex)
                except KeyError:
                    vertex_index = verts_storage.push(vertex)
                finally:
                    tris_indices.append(vertex_index)
                    num_indices += 1

        return (
            verts_storage.vertices, verts_storage.num_verts,
            tris_indices, num_indices
        )


    def process_e3d(self, vertices_e3d):
        pass

    def _smooth_vertex_normal(self, smooth_group, location, triangles, tris_normals, begin_index):
        common_verts_identifiers = []
        normal = mathutils.Vector((0, 0, 0))

        for triangle_index, triangle in enumerate(triangles[begin_index:], start=begin_index):

            if triangle.smooth != smooth_group:
                continue

            for local_vertex_index, vertex in enumerate(triangle.vertices):
                if _compare_vectors(vertex.location, location):
                    normal = normal + tris_normals[triangle_index]
                    common_verts_identifiers.append((triangle_index, local_vertex_index))

        for triangle_index, local_vertex_index in common_verts_identifiers:
            triangles[triangle_index].vertices[local_vertex_index].normal = normal

        return normal


    def _calc_triangles_normals(self, triangles):
        normals = []

        for triangle in triangles:
            edge01 = mathutils.Vector(triangle.vertices[0].location - triangle.vertices[1].location)
            edge02 = mathutils.Vector(triangle.vertices[0].location - triangle.vertices[2].location)

            normal = edge01.cross(edge02)
            if normal.length_squared > 0:
                normal.normalize()
            else:
                normal.zero()

            normals.append(normal)

        return normals


class VertexStorageSectored:
    def __init__(self):
        self._vertices_sectors = {}
        self.vertices = []
        self.num_verts = 0

    def push(self, vertex):
        sector = self.get_sector(vertex.location)

        self.vertices.append(vertex)

        vertex_index = self.num_verts
        sector[vertex_index] = vertex
        self.num_verts += 1

        print("add index", vertex_index)

        return vertex_index

    def find(self, vertex):
        print("finding vertex", vertex)
        sector = self.get_sector(vertex.location)
        for vertex_index, vertex_candidate in sector.items():
            print("...")
            if _compare_vectors(vertex_candidate.location, vertex.location):
                if _compare_vectors(vertex_candidate.normal, vertex.normal):
                    if _compare_vectors(vertex_candidate.mapping, vertex.mapping):
                        print("found", vertex_index)
                        return vertex_index

        raise KeyError(f"{vertex} not exists in given sector {sector}")

    def get_sector(self, vector):
        sector_key = tuple(round(v, ndigits=2) for v in vector)
        sector = self._vertices_sectors.get(sector_key)

        print("sector", sector_key)

        if not sector:
            sector = self._vertices_sectors[sector_key] = {}

        return sector


def _compare_vectors(vec1, vec2, threshold=0.00001):
    vec = vec1 - vec2
    return all(abs(x) < threshold for x in vec)

