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

    def set_name(self, name=None, remove_name_suffixes=False):
        if name is None:
            self.submodel.name = (
                remove_name_suffix(self.obj.name) if self.obj.name.startswith("smokesource")
                else self.obj.name
            )
        else:
            self.submodel.name = name

        if remove_name_suffixes:
            self.submodel.name = remove_name_suffix(self.submodel.name)

    def set_parent_name(self, override=None, remove_name_suffixes=False):
        if override is None:
            if self.obj.parent:
                self.submodel.parent_name = self.obj.parent.name
        else:
            self.submodel.parent_name = override

        if remove_name_suffixes:
            self.submodel.parent_name = remove_name_suffix(self.submodel.parent_name)

    def set_diffuse_color(self, override=None):
        if override is None:
            self.submodel.diffuse_color = self.obj.t3d_properties.diffuse_color * 255
        else:
            self.submodel.diffuse_color = override

    def set_anim(self, override=None):
        if override is None:
            self.submodel.anim = self.obj.t3d_properties.anim
        else:
            self.submodel.anim = override

    def set_selfillum(self, override=None):
        if override is None:
            self.submodel.selfillum = self.obj.t3d_properties.selfillum
        else:
            self.submodel.selfillum = override

    def set_max_distance(self, override=None):
        if override is None:
            self.submodel.max_distance = self.obj.t3d_properties.max_distance
        else:
            self.submodel.max_distance = override

    def set_min_distance(self, override=None):
        if override is None:
            self.submodel.min_distance = self.obj.t3d_properties.min_distance
        else:
            self.submodel.min_distance = override

    def set_transform(self, override=None):
        if override is None:
            mat = self.obj.matrix_local.transposed()

            self.submodel.transform = [
                *mat[0], *mat[1], *mat[2], *mat[3]
            ]
        else:
            self.submodel.transform = override


class MeshOutputBuilder(SubmodelOutputBuilder):
    def __init__(self, obj):
        super().__init__(obj)
        self.submodel = eu07_tools.t3d.create_submodel("Mesh", "MeshSubmodel")

    def set_ambient_color(self, override=None):
        if override is None:
            self.submodel.ambient_color = self.obj.t3d_properties.ambient_color * 255
        else:
            self.submodel.ambient_color = override

    def set_specular_color(self, override=None):
        if override is None:
            self.submodel.specular_color = self.obj.t3d_properties.specular_color * 255
        else:
            self.submodel.specular_color = override

    def set_wire(self, override=None):
        if override is None:
            self.submodel.wire = self.obj.t3d_properties.wire
        else:
            self.submodel.wire = override

    def set_wire_size(self, override=None):
        if override is None:
            self.submodel.wire_size = self.obj.t3d_properties.wire_size
        else:
            self.submodel.wire_size = override

    def set_opacity(self, override=None):
        if override is None:
            self.submodel.opacity = self.obj.t3d_properties.opacity
        else:
            self.submodel.opacity = override

    def set_map(self, override=None, slot_index=None, embed_skins=False, use_generated_img_name=False):
        if override is not None:
            self.submodel.map = override
            return

        if slot_index is not None and len(self.obj.material_slots) > 0:
            mtl = self.obj.data.materials[slot_index]
        else:
            mtl = self.obj.active_material

        is_replacable = self.obj.t3d_properties.replacableskin_id != "None"

        wrapper = MaterialWrapper(mtl)
        if mtl and use_generated_img_name:
            diffusemap = wrapper.get_diffusemap()

            if diffusemap and diffusemap.source == 'GENERATED':
                self.submodel.map = diffusemap.name.replace(".", "_")
                return

        print(self.obj.name, is_replacable)
        if is_replacable and not embed_skins:
            self.submodel.map = self.obj.t3d_properties.replacableskin_id

            print(self.submodel.map.type)
            return

        shortpath = get_shortpath_from_material(mtl)
        self.submodel.map.resource_path = shortpath

        traits = wrapper.get_traits_string()
        self.submodel.map.set_traits_from_str(traits)

    def set_geometry(self, apply_modifiers=True, material_index=None):
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
            if material_index is not None and poly.material_index != material_index:
                continue

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
        self.submodel = eu07_tools.t3d.create_submodel("Mesh", "Banan")

    def set_map(self, override=None, embed_skins=False, use_generated_img_name=False):
        if override is None:
            self.submodel.map = "none"
        else:
            self.submodel.map = override

    def set_geometry(self, apply_modifiers=True, material_index=None):
        # "Banan" is a mesh without mesh_data, so no implementation here
        pass


class FreeSpotLightOutputBuilder(SubmodelOutputBuilder):
    def __init__(self, obj):
        super().__init__(obj)
        self.submodel = eu07_tools.t3d.create_submodel("FreeSpotLight", "SpotSubmodel")

    def set_diffuse_color(self, override=None):
        if override is None:
            self.submodel.diffuse_color = self.obj.data.color * 255
        else:
            self.submodel.diffuse_color = override

    def set_selfillum(self, override=None):
        if override is None:
            self.submodel.selfillum = self.obj.t3d_properties.selfillum_spot
        else:
            self.submodel.selfillum = override

    def set_near_atten_start(self, override=None):
        if override is None:
            self.submodel.near_atten_start = self.obj.t3d_properties.near_atten_start
        else:
            self.submodel.near_atten_start = override

    def set_near_atten_end(self, override=None):
        if override is None:
            self.submodel.near_atten_end = self.obj.t3d_properties.near_atten_end
        else:
            self.submodel.near_atten_end = override

    def set_use_near_atten(self, override=None):
        if override is None:
            self.submodel.use_near_atten = self.obj.t3d_properties.use_near_atten
        else:
            self.submodel.use_near_atten = override

    def set_far_atten_decay_type(self, override=None):
        if override is None:
            self.submodel.far_atten_decay_type = self.obj.t3d_properties.far_atten_decay_type
        else:
            self.submodel.far_atten_decay_type = override

    def set_far_decay_radius(self, override=None):
        if override is None:
            self.submodel.far_decay_radius = self.obj.t3d_properties.far_decay_radius
        else:
            self.submodel.far_decay_radius = override

    def set_falloff_angle(self, override=None):
        if override is None:
            self.submodel.falloff_angle = math.degrees(self.obj.data.spot_size)
        else:
            self.submodel.falloff_angle = override

    def set_hotspot_angle(self, override=None):
        if override is None:
            self.submodel.hotspot_angle = math.degrees(self.obj.data.spot_size * (1 - self.obj.data.spot_blend))
        else:
            self.submodel.hotspot_angle = override

class StarsOutputBuilder(SubmodelOutputBuilder):
    def __init__(self, obj):
        super().__init__(obj)
        self.submodel = eu07_tools.t3d.create_submodel("Stars", "StarsSubmodel")

    def set_points(self, **kwargs):
        points = [
            c for c in self.obj.children
            if c.type == 'LIGHT' and c.data.type == 'POINT'
        ]

        for point in points:
            self.submodel.stars.new(
                point.location,
                [x * 255 for x in point.data.color[:3]]
            )