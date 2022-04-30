import eu07_tools
import eu07_tools.utils.structures.mesh_geometry
from eu07_tools.utils.structures.mesh_geometry import SmoothGroupsNormalCalculator


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
        geometry_data = SmoothGroupsNormalCalculator().run(triangles)
        return cls(*geometry_data)

    @classmethod
    def from_e3d(cls, vertices_e3d):
        geometry_data = SmoothGroupsNormalCalculator().process_e3d(vertices_e3d)
        return cls(*geometry_data)

    @classmethod
    def from_indexed_t3d(cls, vertices, num_verts, tri_indices, num_indices):
        # TODO: This is quick implementation, it adds some overhead with creating MeshTriangle instances.
        # Geometry processor's methods should be splitted to avoid it.
        triangles = []
        for i in range(num_indices // 3):
            indices = tri_indices[i*3:i*3+3]
            verts = [vertices[idx] for idx in indices]
            triangle = eu07_tools.utils.structures.mesh_geometry.MeshTriangle(verts, smooth=-1)
            triangles.append(triangle)

        geometry_data = SmoothGroupsNormalCalculator().run(triangles)

        return cls(*geometry_data)



