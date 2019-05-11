import bpy

from eu07_tools import t3d



class SubmodelOutputBuilder:
    def __init__(self, obj):
        self.obj = obj

    def get_parent(self):
        if self.obj.parent:
            return self.obj.parent.name
        else:
            return "none"

    def get_name(self):
        return self.obj.name

    def get_diffuse(self):
        return self.obj.t3d_properties.diffuse

    def get_anim(self):
        return self.obj.t3d_properties.anim

    def get_max_distance(self):
        return self.obj.t3d_properties.max_distance

    def get_min_distance(self):
        return self.obj.t3d_properties.min_distance

    def get_transform(self):
        # TODO: Local? Really? 
        mat = self.obj.matrix_local.transposed()

        # TODO: Maybe better decomposition can be achieved
        return list(mat[0]) + list(mat[1]) + list(mat[2]) + list(mat[4])

    
class MeshOutputBuilder(SubmodelOutputBuilder):
    def __init__(self, obj):
        super().__init__(obj)

    def get_ambient(self):
        return self.obj.t3d_properties.get_ambient
    
    def get_specular(self):
        return self.obj.t3d_properties.specular

    def get_wire(self):
        return self.obj.t3d_properties.wire

    def get_wire_size(self):
        return self.obj.t3d_properties.wire_size

    def get_opacity(self):
        return self.obj.t3d_properties.opacity

    def get_map(self):
        pass

    def get_geometry(self):
        self.obj.modifiers.new("T3DTriangulation", type='TRIANGULATE')
        mesh = self.obj.to_mesh(bpy.context.scene, True, 'PREVIEW')

        try:
            self._get_geometry_from_mesh(mesh)
        except:
            pass
        finally:
            self.obj.modifiers.remove("T3DTriangulation")

    def _get_geometry_from_mesh(self, mesh):
        smooth_groups = mesh.calc_smooth_groups(True)
        uv_layer = mesh.uv_layers.active
        use_normals = self.obj.t3d_properties.use_normals

        for polygon in mesh.polygons:
            smooth = -1 if use_normals else smooth_groups[0][polygon.index]

            for local_vert_idx, global_vert_idx in enumerate(polygon.vertices):
                vertex = mesh.vertices[global_vert_idx]

                xyz = vertex.co
                ijk = [] if use_normals else vertex.normal

                if uv_layer:
                    mesh_loop_idx = polygon.loop_indices[local_vert_idx]
                    uv = uv_layer.data[mesh_loop_idx].uv
                else:
                    uv = [0, 0]


class FreeSpotLightOutputBuilder(SubmodelOutputBuilder):
    def __init__(self, obj):
        super().__init__(obj)

    def get_diffuse(self):
        return self.obj.data.color

    def get_near_atten_start(self):
        return self.obj.t3d_properties.near_atten_start
    
    def get_near_atten_end(self):
        return self.obj.t3d_properties.near_atten_end

    def get_use_near_atten(self):
        return self.obj.t3d_properties.use_near_atten

    def get_far_atten_decay_type(self):
        return self.obj.t3d_properties.far_atten_decay_type

    def get_far_decay_radius(self):
        return self.obj.data.distance

    def get_falloff_angle(self):
        return self.obj.data.spot_size * (self.obj.data.spot_blend + 1))

    def get_hotspot_angle(self):
        return math.degrees(self.obj.data.spot_size)