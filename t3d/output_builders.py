import bpy

from eu07_tools import t3d

def build_submodel_from_object(obj, config):
    builder = _get_builder(obj, config)

    builder.set_parent()
    builder.set_diffuse()
    builder.set_anim()
    builder.set_selfillum()
    builder.set_max_distance()
    builder.set_min_distance()
    builder.set_transform()

    submodel_type = builder.submodel.submodel_type

    if submodel_type == "Mesh":
        builder.set_ambient()
        builder.set_specular()
        builder.set_wire()
        builder.set_wire_size()
        builder.set_opacity()
        builder.set_map()
        builder.set_geometry()
    elif submodel_type == "FreeSpotLight":
        builder.set_near_atten_start()
        builder.set_near_atten_end()
        builder.set_use_near_atten()
        builder.set_far_atten_decay_type()
        builder.set_far_decay_radius()
        builder.set_falloff_angle()
        builder.set_hotspot_angle()
    elif submodel.type == "Stars":
        builder.set_geometry()




def _get_builder(obj, config):
    if obj.type == 'MESH'
        c = MeshOutputBuilder
    elif obj.type == 'LIGHT' and obj.data.type == 'SPOT':
        c = FreeSpotLightOutputBuilder
    elif obj.type == 'EMPTY':
        pass
    else:
        return None

    return c(obj, config)
        

class SubmodelOutputBuilder:
    def __init__(self, obj, config):
        self.obj = obj
        self.config = config

    def set_parent(self):
        self.submodel.parent_name = (
            self.obj.parent.name if self.obj.parent 
            else "none"
        )

    def set_diffuse(self):
        self.submodel.diffuse = self.obj.t3d_properties.diffuse

    def set_anim(self):
        self.submodel.anim = self.obj.t3d_properties.anim

    def set_selfillum(self):
        self.submodel.selfillum = self.obj.t3d_properties.selfillum

    def set_max_distance(self):
        self.submodel.max_distance = self.obj.t3d_properties.max_distance

    def set_min_distance(self):
        self.submodel.min_distance = self.obj.t3d_properties.min_distance

    def set_transform(self):
        mat = self.obj.matrix_local.transposed()

        self.submodel.transform = [
            *mat[0], *mat[1], *mat[2], *mat[4]
        ]

    
class MeshOutputBuilder(SubmodelOutputBuilder):
    def __init__(self, obj, config):
        super().__init__(obj, config)
        self.submodel = t3d.create_submodel(obj.name, "Mesh")

    def set_ambient(self):
        self.submodel.ambient = self.obj.t3d_properties.set_ambient
    
    def set_specular(self):
        self.submodel.specular = self.obj.t3d_properties.specular

    def set_wire(self):
        self.submodel.wire = self.obj.t3d_properties.wire

    def set_wire_size(self):
        self.submodel.wire_size = self.obj.t3d_properties.wire_size

    def set_opacity(self):
        self.submodel.opacity = self.obj.t3d_properties.opacity

    def set_map(self):
        pass

    def set_geometry(self):
        self.obj.modifiers.new("T3DTriangulation", type='TRIANGULATE')
        mesh = self.obj.to_mesh(bpy.context.scene, True, 'PREVIEW')

        try:
            self._set_geometry_from_mesh(mesh)
        except:
            pass
        finally:
            self.obj.modifiers.remove("T3DTriangulation")

    def _set_geometry_from_mesh(self, mesh):
        smooth_groups = mesh.calc_smooth_groups(True)
        uv_layer = mesh.uv_layers.active
        use_normals = self.obj.t3d_properties.use_normals

        for polygon in mesh.polygons:
            smooth = -1 if use_normals else smooth_groups[0][polygon.index]

            vertices = []
            for local_vert_idx, global_vert_idx in enumerate(polygon.vertices):
                vertex = mesh.vertices[global_vert_idx]

                xyz = vertex.co
                ijk = [] if use_normals else vertex.normal

                if uv_layer:
                    mesh_loop_idx = polygon.loop_indices[local_vert_idx]
                    uv = uv_layer.data[mesh_loop_idx].uv
                else:
                    uv = [0, 0]

                vertices.append((*xyz, *ijk, *uv))

            self.submodel.add_triangle(vertices, smooth)


class FreeSpotLightOutputBuilder(SubmodelOutputBuilder):
    def __init__(self, obj, config):
        super().__init__(obj, config)
        self.submodel = t3d.create_submodel(obj.name, "FreeSpotLight")

    def set_diffuse(self):
        self.submodel.diffuse = self.obj.data.color

    def set_near_atten_start(self):
        self.submodel.near_atten_start = self.obj.t3d_properties.near_atten_start
    
    def set_near_atten_end(self):
        self.submodel.near_atten_end = self.obj.t3d_properties.near_atten_end

    def set_use_near_atten(self):
        self.submodel.use_near_atten = self.obj.t3d_properties.use_near_atten

    def set_far_atten_decay_type(self):
        self.submodel.far_atten_decay_type = self.obj.t3d_properties.far_atten_decay_type

    def set_far_decay_radius(self):
        self.submodel.far_decay_radius = self.obj.data.distance

    def set_falloff_angle(self):
        self.submodel.falloff_angle = self.obj.data.spot_size * (self.obj.data.spot_blend + 1))

    def set_hotspot_angle(self):
        self.submodel.hotspot_angle = math.degrees(self.obj.data.spot_size)


class StarsOutputBuilder(SubmodelOutputBuilder):
    def __init__(self, obj, config):
        super().__init__(obj, config)
        self.submodel = t3d.create_submodel(obj.name, "Stars")

    def set_geometry(self):
        stars = [
            c for c in self.obj.children 
            if c.type == 'LAMP' and c.data.type == 'POINT'
        ]

        for star in stars:
            self.submodel.add_star(star.location, star.data.color)