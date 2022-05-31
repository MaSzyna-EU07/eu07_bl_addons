class GeometryManager:
    def __init__(self):
        self.prefix = ""

    def get(self, entity_props):
        pass

    def get_from_entity(self, entity):
        pass

    def set(self, entity, geometry):
        pass

    def create(self, entity_props):
        pass

    def _make_faces(self, verts, uvs, material_index, num_faces, flip_normal=False):
        for i in range(num_faces):
            vindex_start, vindex_end = i * 2, i * 2 + 4
            face_verts = verts[vindex_start:vindex_end]
            face_uvs = uvs[vindex_start:vindex_end]

            # flipping vert order to generate a face with normal pointing outwards
            face_verts[:2] = reversed(face_verts[:2])
            face_uvs[:2] = reversed(face_uvs[:2])

            face = self.mesh.faces.new(face_verts)
            face.material_index = material_index

            for vertex_index, loop in enumerate(face.loops):
                loop[self.uv_layer].uv = face_uvs[vertex_index]

            if flip_normal:
                face.normal_flip()