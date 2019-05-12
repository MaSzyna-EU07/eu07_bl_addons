import abc
import math
import os

import bmesh
import bpy


def build_object_from_submodel(submodel, config):
    builder = _get_builder(submodel.submodel_type, config)
    submodel_type_lower = submodel.submodel_type.lower() 

    builder.create_submodel(submodel.name)
    builder.set_parent(submodel.parent_name)
    builder.set_anim(submodel.anim)
    builder.set_diffuse(submodel.diffuse)
    builder.set_selfillum(submodel.selfillum)
    builder.set_max_distance(submodel.max_distance)
    builder.set_min_distance(submodel.min_distance)
    builder.set_transform(submodel.transform)

    if submodel_type_lower == 'mesh':
        builder.set_ambient(submodel.ambient)
        builder.set_specular(submodel.specular)
        builder.set_wire(submodel.wire)
        builder.set_wire_size(submodel.wire_size)
        builder.set_opacity(submodel.opacity)
        builder.set_map(submodel.map)
        builder.set_geometry(submodel.triangles)

    elif submodel_type_lower == 'freespotlight':
        builder.set_near_atten_start(submodel.near_atten_start)
        builder.set_near_atten_end(submodel.near_atten_end)
        builder.set_use_near_atten(submodel.use_near_atten)
        builder.set_far_atten_decay_type(submodel.far_atten_decay_type)
        builder.set_far_decay_radius(submodel.far_decay_radius)
        builder.set_falloff_angle(submodel.falloff_angle)
        builder.set_hotspot_angle(submodel.hotspot_angle)

    elif submodel_type_lower == 'stars':
        pass
        

def _get_builder(type_name, config):
    type_name = type_name.lower()

    if type_name == 'mesh':
        cls = MeshInputBuilder
    elif type_name == 'freespotlight':
        cls = FreeSpotLightInputBuilder
    elif type_name == 'stars':
        cls = StarsInputBuilder
    else:
        raise ValueError('Unrecognized submodel type: {0}'.format(type_name))

    return cls(config)


class SubmodelInputBuilder(abc.ABC):
    def __init__(self, config):
        self._config = config

    def create_submodel(self, name):
        self._obj = None

    def set_parent(self, parent_name):
        self._obj.parent = bpy.data.objects.get(parent_name)

    def set_diffuse(self, diffuse):
        pass

    def set_selfillum(self, selfillum):
        self._obj.t3d_properties.selfillum = selfillum

    def set_anim(self, anim):
        self._obj.t3d_properties.anim = anim

    def set_max_distance(self, max_distance):
        self._obj.t3d_properties.max_distance = max_distance

    def set_min_distance(self, min_distance):
        self._obj.t3d_properties.min_distance = min_distance

    def set_transform(self, transform):
        self._obj.matrix_basis = [
            transform[:4],
            transform[4:8],
            transform[8:12],
            transform[12:]
        ]

class MeshInputBuilder(SubmodelInputBuilder):
    def __init__(self, config):
        super().__init__(config)

    def create_submodel(self, name: str):
        mesh = bpy.data.meshes.new(name)
        self._obj = bpy.data.objects.new(name, mesh)
        self._mtl = self._obj.active_material = bpy.data.materials.new(name + "_material")
        self._mtl.use_nodes = True

        bpy.context.scene.collection.objects.link(self._obj)

    def set_ambient(self, ambient):
        self._obj.t3d_properties.ambient = ambient

    def set_diffuse(self, diffuse):
        self._obj.t3d_properties.diffuse = diffuse

    def set_specular(self, specular):
        self._obj.t3d_properties.specular = specular

    def set_wire(self, wire):
        self._obj.t3d_properties.wire = wire

    def set_wire_size(self, wire_size):
        self._obj.t3d_properties.wire_size = wire_size

    def set_opacity(self, opacity):
        self._obj.t3d_properties.opacity = opacity

    def set_map(self, map_: str):
        # TODO: Load materials
        if map_ in "-1 -2 -3 -4 replacableskin":
            full_path = self._config["skins"][map_]
        elif map_ == "none":
            full_path = ""
        else:
            full_path = self._config["asset_searcher"].textures_finder.find(map_)

        if full_path != "":
            try:
                img = bpy.data.images.load(full_path, check_existing=True)
            except:
                pass

            bsdf = self._mtl.node_tree.nodes.get("Principled BSDF")
            # TODO: Bind specular to submodel panel?
            bsdf.inputs[5].default_value = 0

            texture_node = self._mtl.node_tree.nodes.new("ShaderNodeTexImage")
            texture_node.name = texture_node.label = "texture_diffuse"
            texture_node.image = img
            texture_node.location = (-300, 200)

            self._mtl.node_tree.links.new(
                texture_node.outputs[0],
                bsdf.inputs[0]
            )

            if full_path.endswith(".dds"):
                texture_node.texture_mapping.scale[1] = -1


    def set_geometry(self, geometry):
        bm = bmesh.new()
        uv_layer = bm.loops.layers.uv.new()

        for triangle in geometry:
            bm_vertices = []

            for vertex in triangle.vertices:
                bm_vertex = bm.verts.new(vertex.location)
                if vertex.has_normal:
                    bm_vertex.normal = vertex.normal

                bm_vertices.append(bm_vertex)

            bm_face = bm.faces.new(bm_vertices)
            bm_face.smooth = (triangle.smooth > 0)

            for vertex_index, loop in enumerate(bm_face.loops):
                loop[uv_layer].uv = triangle.vertices[vertex_index].mapping

        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.00001)
        bm.to_mesh(self._obj.data)
        bm.free()


class FreeSpotLightInputBuilder(SubmodelInputBuilder):
    def create_submodel(self, name: str):
        data = bpy.data.lights.new(name, type='SPOT')
        self._obj = bpy.data.objects.new(name, data)
        bpy.context.scene.collection.objects.link(self._obj)

    def set_diffuse(self, diffuse):
        self._obj.data.color = _normalize_color(diffuse)

    def set_near_atten_start(self, near_atten_start):
        self._obj.t3d_properties.near_atten_start = near_atten_start

    def set_near_atten_end(self, near_atten_end):
        self._obj.t3d_properties.near_atten_end = near_atten_end

    def set_use_near_atten(self, use_near_atten):
        self._obj.t3d_properties.use_near_atten = use_near_atten

    def set_far_atten_decay_type(self, far_atten_decay_type):
        self._obj.t3d_properties.far_atten_decay_type = far_atten_decay_type

    def set_far_decay_radius(self, far_decay_radius):
        self._obj.data.distance = far_decay_radius

    def set_falloff_angle(self, falloff_angle):
        pass  # TODO: Nice way to set spot_blend

    def set_hotspot_angle(self, hotspot_angle):
        self._obj.data.spot_size = math.radians(hotspot_angle)


class StarsInputBuilder(SubmodelInputBuilder):
    def create_submodel(self, name: str):
        self._obj = bpy.data.objects.new(name, None)
        bpy.context.scene.collection.objects.link(self._obj)

    def set_diffuse(self, diffuse):
        self._obj.t3d_properties.diffuse_color = diffuse

    def set_vertex_groups(self, vertex_groups):
        for vertex_group in vertex_groups:
            for star_array in vertex_group[1:]:

                point = bpy.data.lamps.new(
                    f"{self._obj.name}.star",
                    'POINT'
                )
                star = bpy.data.objects.new(point.name, point)
                bpy.context.scene.objects.link(star)

                star.location = star_array[:3]

                color = int(star_array[3])
                point.color = (
                    ((color) & 0xff) / 255.0,
                    ((color >> 8) & 0xff) / 255.0,
                    ((color >> 16) & 0xff) / 255.0
                )

                star.parent = self._obj


def _normalize_color(color):
    return [value / 255 for value in color]
