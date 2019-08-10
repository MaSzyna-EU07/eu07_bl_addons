import math
import abc
from pathlib import Path

import bpy
import bmesh
import eu07_tools

def export_model(objects, collections, file, config):
    
    objects = _sort_objects(objects)

    if config.use_selection:
        t3d = [_build_submodel(o, config) for o in objects if o.select]
    else:
        t3d = [_build_submodel(o, config) for o in objects]

    for collection in collections:
        if collection.name.startswith("include"):
            path, *parameters = collection.name.split(" ")[1:-1]
            include = eu07_tools.t3d.create_include(path, parameters)
            t3d.append(include)

            if config.export_include_collections:
                outpath = Path(config.root, collection.name.replace("\\", "/").split(" ")[1])
                with open(outpath, "w+", encoding="windows-1250", newline="\r\n") as inc_file:
                    export_model(collection.objects, collection.children, inc_file, config)
                    
    eu07_tools.t3d.dump(t3d, file)

def _sort_objects(objects):
    output = []

    root_level_objects = [o for o in objects if o.parent is None]
    for o in root_level_objects:
        output.append(o)
        output.extend(_get_descendants(o))

    return output

def _get_descendants(o):
    for c in o.children:
        yield c
        yield from _get_descendants(c)
        

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

    return builder.submodel


def _get_builder(obj, config):
    if obj.type == 'MESH':
        c = MeshOutputBuilder
    elif obj.type == 'LIGHT' and obj.data.type == 'SPOT':
        c = FreeSpotLightOutputBuilder
    elif obj.type == 'EMPTY':
        pass
    else:
        return None

    return c(obj, config)
        

class SubmodelOutputBuilder(abc.ABC):
    def __init__(self, obj, config):
        self.obj = obj
        self.config = config
        self.submodel = None

    def set_parent(self):
        self.submodel.parent_name = (
            self.obj.parent.name if self.obj.parent 
            else "none"
        )

    def set_diffuse(self):
        self.submodel.diffuse_color = self.obj.t3d_properties.diffuse_color

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
        self.submodel.ambient_color = self.obj.t3d_properties.ambient_color
    
    def set_specular(self):
        self.submodel.specular_color = self.obj.t3d_properties.specular_color

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

        if mtl:
            if mtl.use_nodes:
                texture_node = mtl.node_tree.nodes.get("texture_diffuse")
                if texture_node:
                    self.submodel.map = eu07_tools.utils.shorten_asset_path(
                        texture_node.image.filepath
                    )

    def set_geometry(self):
        mesh = self.obj.data.copy()
        self._set_geometry_from_mesh(mesh)

    def _set_geometry_from_mesh(self, mesh):
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        bm.to_mesh(mesh)
        bm.free()

        smooth_groups = mesh.calc_smooth_groups(use_bitflags=True)[0]
        uv_layer = mesh.uv_layers.active
        use_normals = self.obj.t3d_properties.use_normals

        for polygon in mesh.polygons:

            if use_normals:
                smooth = -1
            elif polygon.use_smooth:
                smooth = smooth_groups[polygon.index]
            else:
                smooth = 0

            vertices = []
            for local_vert_idx, global_vert_idx in enumerate(polygon.vertices):
                vertex = mesh.vertices[global_vert_idx]

                xyz = vertex.co
                ijk = vertex.normal if use_normals else []

                if uv_layer:
                    mesh_loop_idx = polygon.loop_indices[local_vert_idx]
                    uv = uv_layer.data[mesh_loop_idx].uv
                else:
                    uv = [0, 0]

                vertices.append((*xyz, *ijk, *uv))

            self.submodel.triangles.new(vertices, smooth)



class FreeSpotLightOutputBuilder(SubmodelOutputBuilder):
    def __init__(self, obj, config):
        super().__init__(obj, config)
        self.submodel = eu07_tools.t3d.create_submodel("FreeSpotLight", obj.name)

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
        self.submodel.falloff_angle = (self.obj.data.spot_size * (self.obj.data.spot_blend + 1))

    def set_hotspot_angle(self):
        self.submodel.hotspot_angle = math.degrees(self.obj.data.spot_size)


class StarsOutputBuilder(SubmodelOutputBuilder):
    def __init__(self, obj, config):
        super().__init__(obj, config)
        self.submodel = eu07_tools.t3d.create_submodel("Stars", obj.name)

    def set_geometry(self):
        stars = [
            c for c in self.obj.children 
            if c.type == 'LAMP' and c.data.type == 'POINT'
        ]

        for star in stars:
            self.submodel.stars.new(star.location, star.data.color)