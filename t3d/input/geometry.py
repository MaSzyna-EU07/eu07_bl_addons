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
        self.raw_verts_storage = VertexStorageSectored()
        tris_normals = []
        self.smooth_groups = []

        # Pushing vertices to lookup-optimized storage and calculating triangle normals
        for triangle_index, triangle in enumerate(triangles):

            normal = self._calc_triangle_normal(triangle)
            tris_normals.append(normal)

            self.smooth_groups.append(triangle.smooth)

            for vertex in triangle.vertices:
                self.raw_verts_storage.push(vertex)

        # Calculating per-face vertex normals
        per_face_vertex_normals = []
        self.precalculated_smooth_normals = {}
        for triangle_index, triangle in enumerate(triangles):
            triangle_normal = tris_normals[triangle_index]

            for local_vert_index, vertex in enumerate(triangle.vertices):
                vertex_index = triangle_index * local_vert_index

                try:
                    per_face_vertex_normals.append(self.precalculated_smooth_normals[vertex_index])
                except KeyError:

                    if triangle.smooth == -1:
                        per_face_vertex_normals.append(vertex.normal)

                    elif triangle.smooth == 0:
                        per_face_vertex_normals.append(triangle_normal)

                    else:
                        normal, shared_indices = self._calc_smooth_group_normal(vertex, triangle.smooth)
                        per_face_vertex_normals.append(normal)

                        for shared_index in shared_indices:
                            self.precalculated_smooth_normals[shared_index] = normal

        return [], 0, [], 0

    def _calc_triangle_normal(self, triangle):
        edge01 = mathutils.Vector(triangle.vertices[0].location - triangle.vertices[1].location)
        edge02 = mathutils.Vector(triangle.vertices[0].location - triangle.vertices[2].location)

        normal = edge01.cross(edge02)
        if normal.length_squared > 0:
            normal.normalize()
        else:
            normal.zero()

        return normal

    def _calc_smooth_group_normal(self, vertex, smooth_group):
        sector = self.raw_verts_storage.get_sector(vertex.location)

        normal = vertex.normal

        for sc_vertex_index, sc_vertex in sector:
            triangle_index = sc_vertex_index // 3
            sc_vertex_smooth_group = self.smooth_groups[triangle_index]

            shared_indices = set()
            if sc_vertex_smooth_group == smooth_group:
                normal = normal + sc_vertex.normal

                shared_indices.add(sc_vertex_index)

        return normal, shared_indices


    def _are_normals_opposite(self, normal1, normal2):
        return mathutils.Vector(normal1).dot(normal2) == -1


    def process_e3d(self, vertices_e3d):
        pass


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
                return vertex_index

        raise KeyError(f"{vertex} not exists in given sector {sector}")

    def __getitem__(self, index):
        return self.vertices[index]

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

