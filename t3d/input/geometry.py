import math

import mathutils

import eu07_tools


class Geometry:
    def __init__(self, num_indices, indices, locations, normals, uvs, smooth_groups):
        self.num_indices = num_indices
        self.indices = indices
        self.locations = locations
        self.per_face_vertex_normals = normals
        self.per_face_uvs = uvs
        self.debug_smooth_groups = smooth_groups

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
    def process_legacy_t3d(self, input_triangles):
        self.verts_storage = VertexStorageSectored()
        self.tris_normals = []
        self.smooth_groups = []
        triangles = []

        # Pushing vertices to lookup-optimized storage and calculating triangle normals
        for triangle_index, triangle in enumerate(input_triangles):
            if _is_degenerate(triangle):
                continue

            triangles.append(triangle)
            normal = self._calc_triangle_normal(triangle)
            self.tris_normals.append(mathutils.Vector(normal))

            self.smooth_groups.append(triangle.smooth)

            for vertex in triangle.vertices:
                self.verts_storage.push(vertex)

        # Calculating per-face vertex normals
        per_face_vertex_normals = []
        self.precalculated_normals = {}
        for triangle_index, triangle in enumerate(triangles):
            triangle_normal = self.tris_normals[triangle_index]

            for local_vert_index, vertex in enumerate(triangle.vertices):
                vertex_index = triangle_index * 3 + local_vert_index

                try:
                    per_face_vertex_normals.append(self.precalculated_normals[vertex_index])
                except KeyError:
                    if triangle.smooth == -1:
                        normal = mathutils.Vector(vertex.normal)
                        normal = normal.normalized() if normal.length_squared > 0 else normal

                    elif triangle.smooth == 0:
                        normal = triangle_normal

                    else:
                        normal, shared_indices = self._calc_smooth_group_normal(
                            vertex, self.tris_normals[triangle_index], triangle.smooth
                        )

                        normal = normal.normalized() if normal.length_squared > 0 else triangle_normal

                        for shared_index in shared_indices:
                            self.precalculated_normals[shared_index] = normal

                    per_face_vertex_normals.append(normal)
                    self.precalculated_normals[vertex_index] = normal



        # Removing duplicated vertices & indexing
        unique_verts_storage = VertexStorageSectored()
        unique_per_face_vertex_normals = []
        unique_per_face_uvs = []
        indexed_geometry = []
        num_indices = 0

        # TODO: There are situations, where random faces are not connected (or are partially connected) to neighbours
        # TODO: Bmesh reports that there are faces, that already exists (seems like 3 indices are repeated somewhere)
        for triangle_index, triangle in enumerate(triangles):
            for local_vert_index, vertex in enumerate(triangle.vertices):
                global_vert_index = triangle_index * 3 + local_vert_index

                try:
                    vertex_index = unique_verts_storage.find(vertex)
                    found_vert_triangle_index = vertex_index // 3
                    if self._are_normals_opposite(
                            self.tris_normals[triangle_index],
                            self.tris_normals[found_vert_triangle_index]
                    ):
                        vertex_index = unique_verts_storage.push(vertex)
                except KeyError:
                    vertex_index = unique_verts_storage.push(vertex)

                indexed_geometry.append(vertex_index)
                unique_per_face_vertex_normals.append(per_face_vertex_normals[global_vert_index])
                unique_per_face_uvs.append(vertex.mapping)
                num_indices += 1

        locations = [vertex.location for vertex in unique_verts_storage]

        return num_indices, indexed_geometry, locations, unique_per_face_vertex_normals, unique_per_face_uvs, self.smooth_groups

    def _calc_triangle_normal(self, triangle):
        edge01 = mathutils.Vector(triangle.vertices[0].location - triangle.vertices[1].location)
        edge02 = mathutils.Vector(triangle.vertices[0].location - triangle.vertices[2].location)

        normal = edge01.cross(edge02)
        if normal.length_squared > 0:
            normal.normalize()
        else:
            normal.zero()

        return normal

    def _calc_smooth_group_normal(self, vertex, initial_normal, smooth_group):
        sector = self.verts_storage.get_sector(vertex.location)

        normal = initial_normal

        shared_indices = set()
        for sc_vertex_index, sc_vertex in sector.items():
            if not _compare_vectors(sc_vertex.location, vertex.location):
                continue
            triangle_index = sc_vertex_index // 3
            sc_vertex_smooth_group = self.smooth_groups[triangle_index]

            if sc_vertex_smooth_group & smooth_group:
                adjacent_normal = self.tris_normals[triangle_index]
                if not self._are_normals_opposite(adjacent_normal, normal):
                    normal = normal + adjacent_normal
                    shared_indices.add(sc_vertex_index)

        return mathutils.Vector(normal).normalized(), shared_indices


    def _are_normals_opposite(self, normal1, normal2):
        return mathutils.Vector(normal1).dot(normal2) < -0.99


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

        return vertex_index

    def find(self, vertex):
        sector = self.get_sector(vertex.location)
        for vertex_index, vertex_candidate in sector.items():
            if _compare_vectors(vertex_candidate.location, vertex.location):
                return vertex_index

        raise KeyError(f"{vertex} not exists in given sector {sector}")

    def __getitem__(self, index):
        return self.vertices[index]

    def __iter__(self):
        return iter(self.vertices)

    def get_sector(self, vector):
        sector_key = tuple(round(v, ndigits=2) for v in vector)
        sector = self._vertices_sectors.get(sector_key)

        if not sector:
            sector = self._vertices_sectors[sector_key] = {}

        return sector


def _compare_vectors(vec1, vec2, threshold=0.00001):
    vec = vec1 - vec2
    return all(abs(x) < threshold for x in vec)

def _is_degenerate(triangle):
    edge1 = mathutils.Vector(triangle.vertices[1].location - triangle.vertices[0].location)
    edge2 = mathutils.Vector(triangle.vertices[2].location - triangle.vertices[0].location)

    return edge1.cross(edge2).length_squared == 0