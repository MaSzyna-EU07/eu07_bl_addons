import abc
import math

import bmesh
import bpy

import eu07_tools
from material_tools.utils import get_shortpath_from_material


def get_builder(obj):
    if obj.type == 'MESH':
        c = MeshOutputBuilder
    elif obj.type == 'LIGHT' and obj.data.type == 'SPOT':
        c = FreeSpotLightOutputBuilder
    elif obj.type == 'EMPTY' and obj.empty_display_type == "PLAIN_AXES":
        c = StarsOutputBuilder
    else:
        return None

    return c(obj)


class SubmodelOutputBuilder(abc.ABC):
    def __init__(self, obj):
        self.obj = obj
        self.submodel = None

    def set_parent(self):
        if self.obj.parent:
            self.submodel.parent_name = self.obj.parent.name
        else:
            return "none"

    def set_diffuse(self):
        self.submodel.diffuse_color = self.obj.t3d_properties.diffuse_color * 255

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
            *mat[0], *mat[1], *mat[2], *mat[3]
        ]


class MeshOutputBuilder(SubmodelOutputBuilder):
    def __init__(self, obj):
        super().__init__(obj)
        self.submodel = eu07_tools.t3d.create_submodel("Mesh", obj.name)

    def set_ambient(self):
        self.submodel.ambient_color = self.obj.t3d_properties.ambient_color * 255

    def set_specular(self):
        self.submodel.specular_color = self.obj.t3d_properties.specular_color * 255

    def set_wire(self):
        self.submodel.wire = self.obj.t3d_properties.wire

    def set_wire_size(self):
        self.submodel.wire_size = self.obj.t3d_properties.wire_size

    def set_opacity(self):
        self.submodel.opacity = self.obj.t3d_properties.opacity

    def set_map(self):
        mtl = self.obj.active_material

        if self.obj.t3d_properties.replacableskin_id != "None":
            self.submodel.map = self.obj.t3d_properties.replacableskin_id
            return

        self.submodel.map = get_shortpath_from_material(mtl)

    def set_geometry(self, apply_modifiers):
        mesh = None

        if apply_modifiers:
            depsgraph = bpy.context.evaluated_depsgraph_get()
            obj_eval = self.obj.evaluated_get(depsgraph)

            mesh = bpy.data.meshes.new_from_object(obj_eval)
        else:
            mesh = self.obj.data.copy()

        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        bm.to_mesh(mesh)
        bm.free()

        uv_layer = mesh.uv_layers.active
        if uv_layer:
            uv_data = uv_layer.data[:]

        if self.obj.t3d_properties.use_face_indices:
            self.submodel.use_indices = True
            mesh.calc_normals_split()
            mesh.calc_tangents()

            for poly in mesh.polygons:
                indices = []

                for loop_index in poly.loop_indices:
                    loop = mesh.loops[loop_index]
                    indices.append(loop.vertex_index)

                self.submodel.indices.extend(indices)

            for vertex in mesh.vertices:
                co = vertex.co
                normal = vertex.normal

                for loop in mesh.loops:
                    if loop.vertex_index == vertex.index:
                        uv = uv_data[loop.index].uv if uv_layer else [0, 0]
                        tangent = [*loop.tangent, 1]

                vertex = self.submodel.vertices.new([*co, *normal, *uv, *tangent])

        else:
            smooth_groups = mesh.calc_smooth_groups(use_bitflags=True)[0]

            use_normals = self.obj.t3d_properties.use_normals

            if use_normals:
                mesh.calc_normals_split()

            for poly in mesh.polygons:
                smooth = 0
                if use_normals:
                    smooth = -1
                elif poly.use_smooth:
                    smooth = smooth_groups[poly.index]

                vertices = []

                for loop_index in poly.loop_indices:
                    loop = mesh.loops[loop_index]

                    pos = mesh.vertices[loop.vertex_index].co
                    normal = loop.normal if use_normals else []
                    uv = uv_data[loop_index].uv if uv_layer else [0, 0]

                    vertices.append((*pos, *normal, *uv))

                self.submodel.triangles.new(vertices, smooth)

        if apply_modifiers:
            bpy.data.meshes.remove(mesh)


class FreeSpotLightOutputBuilder(SubmodelOutputBuilder):
    def __init__(self, obj):
        super().__init__(obj)
        self.submodel = eu07_tools.t3d.create_submodel("FreeSpotLight", obj.name)

    def set_diffuse(self):
        self.submodel.diffuse_color = self.obj.data.color * 255

    def set_selfillum(self):
        self.submodel.selfillum = self.obj.t3d_properties.selfillum_spot

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
        self.submodel.falloff_angle = (self.obj.data.spot_size * (self.obj.data.spot_blend + 1))

    def set_hotspot_angle(self):
        self.submodel.hotspot_angle = math.degrees(self.obj.data.spot_size)


class StarsOutputBuilder(SubmodelOutputBuilder):
    def __init__(self, obj):
        super().__init__(obj)
        self.submodel = eu07_tools.t3d.create_submodel("Stars", obj.name)

    def set_geometry(self):
        points = [
            c for c in self.obj.children
            if c.type == 'LIGHT' and c.data.type == 'POINT'
        ]

        for point in points:
            self.submodel.stars.new(
                point.location,
                [x * 255 for x in point.data.color[:3]]
            )