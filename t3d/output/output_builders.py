import abc
import math

import bmesh
import bpy

import eu07_tools
from material_tools.utils import get_shortpath_from_material
from material_tools.wrapper import MaterialWrapper


def get_builder(obj):
    cls = None

    if obj.type == 'MESH':
        cls = MeshOutputBuilder
    elif obj.type == 'LIGHT' and obj.data.type == 'SPOT':
        cls = FreeSpotLightOutputBuilder
    elif obj.type == 'EMPTY':
        for child in obj.children:
            if child.type == 'LIGHT' and child.data.type == 'POINT':
                cls = StarsOutputBuilder

        not_stars = cls is None

        if not_stars:
            cls = BananMeshOutputBuilder

    return cls(obj) if cls else None


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

        if self.obj.active_material:
            wrapper = MaterialWrapper(self.obj.active_material)

            if wrapper.get_diffusemap() is not None:
                self.submodel.opacity = wrapper.get_opacity()

    def set_map(self, embed_skins=False):
        mtl = self.obj.active_material

        is_replacable = self.obj.t3d_properties.replacableskin_id != "None"

        if is_replacable and not embed_skins:
            self.submodel.map = self.obj.t3d_properties.replacableskin_id
            return

        self.submodel.map = get_shortpath_from_material(mtl)

    def set_geometry(self, apply_modifiers):
        mesh = None

        self.submodel.geometry.to_indexed()

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
        if uv_layer is None:
            uv_layer = mesh.uv_layers.new()

        uv_data = uv_layer.data[:]

        try:
            mesh.calc_tangents(uvmap=uv_layer.name)
        except RuntimeError:
            return

        if not mesh.has_custom_normals:
            mesh.calc_normals_split()


        verts_collector = {}
        vertex_count = 0

        for poly in mesh.polygons:

            for loop_index in poly.loop_indices:
                loop = mesh.loops[loop_index]

                vert_data = []
                vert_data.extend(mesh.vertices[loop.vertex_index].co)
                vert_data.extend(loop.normal)
                vert_data.extend(uv_data[loop_index].uv if uv_layer else [0, 0])
                vert_data.extend([*loop.tangent, 1])

                vert_data = tuple([round(x, 5) for x in vert_data])

                index = verts_collector.get(vert_data)
                if index is None:
                    index = vertex_count
                    verts_collector[vert_data] = index
                    vertex_count += 1

                self.submodel.geometry.indices.append(index)

        for vert_data, index in verts_collector.items():
            self.submodel.geometry.vertices.new(vert_data)

        bpy.data.meshes.remove(mesh)


class BananMeshOutputBuilder(MeshOutputBuilder):
    def __init__(self, obj):
        super().__init__(obj)

        name = obj.name
        if obj.name.startswith("smokesource"):
            name = obj.name.split(".")[0]

        self.submodel = eu07_tools.t3d.create_submodel("Mesh", name)

    def set_map(self, embed_skins=False):
        self.submodel.map = "none"

    def set_geometry(self, apply_modifiers):
        # "Banan" is a mesh without geometry, so no implementation here
        pass


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
        self.submodel.falloff_angle = math.degrees(self.obj.data.spot_size)

    def set_hotspot_angle(self):
        self.submodel.hotspot_angle = math.degrees(self.obj.data.spot_size * (1 - self.obj.data.spot_blend))


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