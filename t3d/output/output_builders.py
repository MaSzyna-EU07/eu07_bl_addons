import abc
import math

import bmesh
import bpy

import eu07_tools
from material_tools.utils import get_shortpath_from_material
from material_tools.wrapper import MaterialWrapper
from common.utils import remove_name_suffix


def get_builder(obj):
    cls = None

    if obj.type in ('MESH', 'CURVE', 'SURFACE', 'META', 'FONT'):
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

    def set_name(self, remove_name_suffixes):
        self.submodel.name = (
            remove_name_suffix(self.obj.name) if (remove_name_suffixes or self.obj.name.startswith("smokesource"))
            else self.obj.name
        )

    def set_parent(self, remove_name_suffixes):
        if self.obj.parent:
            self.submodel.parent_name = (
                remove_name_suffix(self.obj.parent.name) if remove_name_suffixes
                else self.obj.parent.name
            )
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
        self.submodel = eu07_tools.t3d.create_submodel("Mesh", remove_name_suffix(obj.name))

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

    def set_map(self, embed_skins=False, use_generated_img_name=False):
        mtl = self.obj.active_material

        is_replacable = self.obj.t3d_properties.replacableskin_id != "None"

        if mtl and use_generated_img_name:
            wrapper = MaterialWrapper(mtl)
            diffusemap = wrapper.get_diffusemap()

            if diffusemap and diffusemap.source == 'GENERATED':
                self.submodel.map = diffusemap.name.replace(".", "_")
                return

        if is_replacable and not embed_skins:
            self.submodel.map = self.obj.t3d_properties.replacableskin_id
            return

        self.submodel.map = get_shortpath_from_material(mtl)

    def set_geometry(self, apply_modifiers):
        mesh = None
        temp_obj = self.obj

        self.submodel.geometry.to_indexed()

        if apply_modifiers:
            depsgraph = bpy.context.evaluated_depsgraph_get()
            temp_obj = self.obj.evaluated_get(depsgraph)

        mesh = temp_obj.to_mesh()

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


        verts_collector = {}
        vertex_count = 0

        for poly in mesh.polygons:

            for loop_index in poly.loop_indices:
                loop = mesh.loops[loop_index]

                vert_data = []
                vert_data.extend(mesh.vertices[loop.vertex_index].co)
                vert_data.extend(mesh.corner_normals[loop.index].vector)
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

        temp_obj.to_mesh_clear()


class BananMeshOutputBuilder(MeshOutputBuilder):
    def __init__(self, obj):
        super().__init__(obj)
        self.submodel = eu07_tools.t3d.create_submodel("Mesh", obj.name)

    def set_map(self, embed_skins=False, use_generated_img_name=False):
        self.submodel.map = "none"

    def set_geometry(self, apply_modifiers):
        # "Banan" is a mesh without mesh_data, so no implementation here
        pass


class FreeSpotLightOutputBuilder(SubmodelOutputBuilder):
    def __init__(self, obj):
        super().__init__(obj)
        self.submodel = eu07_tools.t3d.create_submodel("FreeSpotLight", remove_name_suffix(obj.name))

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
        self.submodel.far_decay_radius = self.obj.t3d_properties.far_decay_radius

    def set_falloff_angle(self):
        self.submodel.falloff_angle = math.degrees(self.obj.data.spot_size)

    def set_hotspot_angle(self):
        self.submodel.hotspot_angle = math.degrees(self.obj.data.spot_size * (1 - self.obj.data.spot_blend))


class StarsOutputBuilder(SubmodelOutputBuilder):
    def __init__(self, obj):
        super().__init__(obj)
        self.submodel = eu07_tools.t3d.create_submodel("Stars", remove_name_suffix(obj.name))

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