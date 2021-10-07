import abc
import math
from pathlib import Path

import bmesh
import bpy
import eu07_tools

from common import get_path_from_material, get_root



def export_model(objects, file, config):
    objects = HierarchyMaker(objects).make_hierarchy()

    if config.use_selection:
        t3d = [_build_submodel(o, config) for o in objects if o.select_get()]
    else:
        t3d = [_build_submodel(o, config) for o in objects]

    eu07_tools.t3d.dump(t3d, file)


def trim_namespace(name, prefix):
    if prefix:
        if name.startswith(prefix):
            return name[len(prefix):]

    return name


class HierarchyMaker:
    def __init__(self, collection):
        self._collection = collection

    def make_hierarchy(self):
        objects = self._filter_objects(self._collection.objects)

        for o in objects:
            if self._is_orphan(o):
                yield from self._sort_branch(o)

    def _sort_branch(self, first):
        yield first

        children = self._filter_objects(first.children)
        for child in children:
            yield from self._sort_branch(child)

    def _is_orphan(self, o):
        has_parent = o.parent
        parent_not_in_collection = o.parent and (o.parent.name not in self._collection.objects)

        return (not has_parent) or (has_parent and parent_not_in_collection)

    def _filter_objects(self, objects):
        for o in objects:
            is_mesh = (o.type == 'MESH')
            is_freespotlight = (o.type == 'LIGHT' and o.data.type == 'SPOT')

            is_stars_container = (o.type == 'EMPTY' and o.empty_display_type == "PLAIN_AXES")
            has_star_child = (any(c.type == "LIGHT" and c.data.type == "POINT" for c in o.children))
            is_stars = is_stars_container and has_star_child

            if is_mesh or is_freespotlight or is_stars:
                yield o


def _build_submodel(obj, config):
    builder = _get_builder(obj, config)
    
    builder.set_parent()
    builder.set_diffuse()
    builder.set_anim()
    builder.set_selfillum()
    builder.set_max_distance()
    builder.set_min_distance()
    builder.set_transform()

    submodel_type = builder.submodel.type

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
    elif submodel_type == "Stars":
        builder.set_geometry()

    builder.submodel.name = trim_namespace(builder.submodel.name, config.namespace_prefix)

    return builder.submodel


def _get_builder(obj, config):
    if obj.type == 'MESH':
        c = MeshOutputBuilder
    elif obj.type == 'LIGHT' and obj.data.type == 'SPOT':
        c = FreeSpotLightOutputBuilder
    elif obj.type == 'EMPTY' and obj.empty_display_type == "PLAIN_AXES":
        c = StarsOutputBuilder
    else:
        return None

    return c(obj, config)
        

class SubmodelOutputBuilder(abc.ABC):
    def __init__(self, obj, config):
        self.obj = obj
        self.config = config
        self.submodel = None

    def set_parent(self):
        if self.obj.parent:
            self.submodel.parent_name = trim_namespace(self.obj.parent.name, self.config.namespace_prefix)
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
    def __init__(self, obj, config):
        super().__init__(obj, config)
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

        self.submodel.map = get_path_from_material(mtl)

    def set_geometry(self):

        mesh = None

        if (self.config.use_modifiers):
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

        if self.config.use_indices:
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

        if (self.config.use_modifiers):
            bpy.data.meshes.remove(mesh)


class FreeSpotLightOutputBuilder(SubmodelOutputBuilder):
    def __init__(self, obj, config):
        super().__init__(obj, config)
        self.submodel = eu07_tools.t3d.create_submodel("FreeSpotLight", obj.name)

    def set_diffuse(self):
        self.submodel.diffuse_color = self.obj.data.color * 255

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
    def __init__(self, obj, config):
        super().__init__(obj, config)
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