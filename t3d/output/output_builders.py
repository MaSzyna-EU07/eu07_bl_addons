import abc
import math

import bmesh
import bpy

import eu07_tools
from material_tools.utils import get_shortpath_from_material
from material_tools.wrapper import MaterialWrapper
from common.utils import remove_name_suffix
from mathutils import Matrix

from sys import platform
if platform == "linux":
    from native.eu07_tools_native_Linux import MikkContext
elif platform == "win32":
    from native.eu07_tools_native_Windows import MikkContext


def get_builder(exporter, obj):
    cls = None

    if obj.type == 'MESH' and not exporter.flatten_mesh_hierarchy:
        materials = set()
        materials = materials.union(filter(lambda mtl: mtl is not None, map(lambda slot: slot.material, obj.material_slots)))
        if len(materials) <= 1:
            cls = SingleMaterialMeshOutputBuilder
        else:
            cls = MultiMaterialMeshOutputBuilder
    elif obj.type == 'LIGHT' and obj.data.type == 'SPOT':
        cls = FreeSpotLightOutputBuilder
    elif obj.type == 'EMPTY':
        if exporter.flatten_mesh_hierarchy and filter(lambda child: child.type == 'MESH', obj.children):
            materials = set()
            for o in filter(lambda child: child.type == 'MESH', obj.children):
                materials = materials.union(filter(lambda mtl: mtl is not None, map(lambda slot: slot.material, o.material_slots)))
            if len(materials) <= 1:
                cls = SingleMaterialMeshOutputBuilder
            else:
                cls = MultiMaterialMeshOutputBuilder
        else:
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
            
    def type(self):
        return self.submodel.type

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
        
    def submodels(self):
        return [ self.submodel ] if self.submodel is not None else []


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
        pass

    def set_map(self, embed_skins=False, use_generated_img_name=False):
        pass

    def get_meshes(self, apply_modifiers):

        meshes = []

        if self.obj.type == 'MESH':
            mesh_obj = self.obj
            if apply_modifiers:
                depsgraph = bpy.context.evaluated_depsgraph_get()
                obj_eval = mesh_obj.evaluated_get(depsgraph)
    
                mesh = bpy.data.meshes.new_from_object(obj_eval)
            else:
                mesh = mesh_obj.data.copy()
    
            if mesh.uv_layers.active is None:
                self.report({'WARNING'}, "{0} has no active UV layer, skipping object.".format(mesh_obj.name))
                bpy.data.meshes.remove(mesh)
            
            try:
                mesh.calc_normals_split()
                mesh.calc_loop_triangles()
            except:
                bpy.data.meshes.remove(mesh)

            meshes.append((mesh_obj, mesh, Matrix.Identity(4)))
        else:
            for mesh_obj in self.obj.children:
                if mesh_obj.type != 'MESH':
                    continue
            
                if apply_modifiers:
                    depsgraph = bpy.context.evaluated_depsgraph_get()
                    obj_eval = mesh_obj.evaluated_get(depsgraph)
        
                    mesh = bpy.data.meshes.new_from_object(obj_eval)
                else:
                    mesh = mesh_obj.data.copy()
        
                if mesh.uv_layers.active is None:
                    self.report({'WARNING'}, "{0} has no active UV layer, skipping object.".format(mesh_obj.name))
                    bpy.data.meshes.remove(mesh)
                    continue
                
                try:
                    mesh.calc_normals_split()
                    mesh.calc_loop_triangles()
                except:
                    bpy.data.meshes.remove(mesh)
                    continue

                meshes.append((mesh_obj, mesh, mesh_obj.matrix_local))
        
        return meshes

    def set_geometry(self, apply_modifiers):
        mesh = None

        context = MikkContext()

        self.submodel.geometry.to_indexed()

        if apply_modifiers:
            depsgraph = bpy.context.evaluated_depsgraph_get()
            obj_eval = self.obj.evaluated_get(depsgraph)

            mesh = bpy.data.meshes.new_from_object(obj_eval)
        else:
            mesh = self.obj.data.copy()

        if mesh.uv_layers.active is None:
            self.report({'WARNING'}, "{0} has no active UV layer, skipping object.".format(self.obj.name))
            return
        
        try:
            mesh.calc_normals_split()
            mesh.calc_loop_triangles()
        except:
            return
            
        for triangle in mesh.loop_triangles:
                
            for vi in range(3):
                loop_index = triangle.loops[vi]
                loop = mesh.loops[loop_index]
                co = tuple(mesh.vertices[loop.vertex_index].co)
                normal = tuple(loop.normal)
                uv = tuple(mesh.uv_layers.active.data[loop_index].uv)
                
                context.addVertex(co, normal, uv)

        bpy.data.meshes.remove(mesh)
            
        context.calculate()
        (vertices, indices) = context.computeVertexTable()

        self.submodel.geometry.indices = indices
        
        for vert_data in vertices:
            self.submodel.geometry.vertices.new(vert_data)


class MultiMaterialMeshOutputBuilder(MeshOutputBuilder):
    def __init__(self, obj):
        super().__init__(obj)

        materials = set()
        if obj.type == 'MESH':
            materials = set(filter(lambda mtl: mtl is not None, map(lambda slot: slot.material, obj.material_slots)))
        else:
            for o in filter(lambda child: child.type == 'MESH', obj.children):
                materials = materials.union(filter(lambda mtl: mtl is not None, map(lambda slot: slot.material, o.material_slots)))
                
        self.mtl_to_submodels = {}
        for material in materials:
                self.mtl_to_submodels[material] = eu07_tools.t3d.create_submodel("Mesh", remove_name_suffix(material.name))
            
    def type(self):
        return "Mesh"

    def set_name(self, remove_name_suffixes):
        super().set_name(remove_name_suffixes)

        for mtl, submodel in self.mtl_to_submodels.items():
            submodel.name = remove_name_suffix(mtl.name) if remove_name_suffixes else mtl.name
            submodel.parent_name = remove_name_suffix(self.obj.name) if remove_name_suffixes else self.obj.name

    def set_ambient(self):
        for mtl, submodel in self.mtl_to_submodels.items():
            submodel.ambient_color = self.obj.t3d_properties.ambient_color * 255

    def set_specular(self):
        for mtl, submodel in self.mtl_to_submodels.items():
            submodel.specular_color = self.obj.t3d_properties.specular_color * 255

    def set_diffuse(self):
        for mtl, submodel in self.mtl_to_submodels.items():
            submodel.diffuse_color = self.obj.t3d_properties.diffuse_color * 255

    def set_anim(self):
        for mtl, submodel in self.mtl_to_submodels.items():
            submodel.anim = self.obj.t3d_properties.anim

    def set_selfillum(self):
        for mtl, submodel in self.mtl_to_submodels.items():
            submodel.selfillum = self.obj.t3d_properties.selfillum

    def set_max_distance(self):
        for mtl, submodel in self.mtl_to_submodels.items():
            submodel.max_distance = self.obj.t3d_properties.max_distance

    def set_min_distance(self):
        for mtl, submodel in self.mtl_to_submodels.items():
            submodel.min_distance = self.obj.t3d_properties.min_distance

    def set_wire(self):
        for mtl, submodel in self.mtl_to_submodels.items():
            submodel.wire = self.obj.t3d_properties.wire

    def set_wire_size(self):
        for mtl, submodel in self.mtl_to_submodels.items():
            submodel.wire_size = self.obj.t3d_properties.wire_size

    def set_opacity(self):
        for mtl, submodel in self.mtl_to_submodels.items():
            submodel.opacity = self.obj.t3d_properties.opacity

            if mtl and self.obj.t3d_properties.opacity_source == "MATERIAL":
                wrapper = MaterialWrapper(mtl)

                if wrapper.get_diffusemap() is not None:
                    submodel.opacity = wrapper.get_opacity()

    def set_map(self, embed_skins=False, use_generated_img_name=False):
        for mtl, submodel in self.mtl_to_submodels.items():
            
            is_replacable = self.obj.t3d_properties.replacableskin_id != "None"
    
            if mtl and use_generated_img_name:
                wrapper = MaterialWrapper(mtl)
                diffusemap = wrapper.get_diffusemap()
    
                if diffusemap and diffusemap.source == 'GENERATED':
                    submodel.map = diffusemap.name.replace(".", "_")
                    return
    
            if is_replacable and not embed_skins:
                submodel.map = self.obj.t3d_properties.replacableskin_id
                return
    
            submodel.map = get_shortpath_from_material(mtl)

    def set_geometry(self, apply_modifiers):

        meshes = self.get_meshes(apply_modifiers)

        for mtl, submodel in self.mtl_to_submodels.items():
        
            submodel.geometry.to_indexed()
            verts_collector = {}
            vertex_count = 0
            
            context = MikkContext()
                
            for (mesh_obj, mesh, local_transform) in meshes:
                    
                allowed_indices = set(filter(lambda slot : mesh_obj.material_slots[slot].material == mtl, range(len(mesh_obj.material_slots))))
                
                if not allowed_indices:
                    continue
                
                flip_normals = local_transform.determinant() < 0
                    
                for triangle in mesh.loop_triangles:
                    if triangle.material_index not in allowed_indices:
                        continue
                        
                    for vi in (reversed(range(3)) if flip_normals else range(3)):
                        loop_index = triangle.loops[vi]
                        loop = mesh.loops[loop_index]
                        co = tuple(local_transform @ mesh.vertices[loop.vertex_index].co)
                        normal = tuple(local_transform.to_3x3() @ loop.normal)
                        uv = tuple(mesh.uv_layers.active.data[loop_index].uv)
                        
                        context.addVertex(co, normal, uv)
            
            context.calculate()
            (vertices, indices) = context.computeVertexTable()

            submodel.geometry.indices = indices
            
            for vert_data in vertices:
                submodel.geometry.vertices.new(vert_data)

        for (obj, mesh, transform) in meshes:
            bpy.data.meshes.remove(mesh)
        
    def submodels(self):
        result = super().submodels()
        result.extend(self.mtl_to_submodels.values())
        return result

class SingleMaterialMeshOutputBuilder(MeshOutputBuilder):
    def __init__(self, obj):
        super().__init__(obj)

        materials = set()
        if obj.type == 'MESH':
            materials = set(filter(lambda mtl: mtl is not None, map(lambda slot: slot.material, obj.material_slots)))
        else:
            for o in filter(lambda child: child.type == 'MESH', obj.children):
                materials = materials.union(filter(lambda mtl: mtl is not None, map(lambda slot: slot.material, o.material_slots)))

        self.material = next(iter(materials)) if len(materials) else None
        
        self.submodel = eu07_tools.t3d.create_submodel("Mesh", remove_name_suffix(obj.name))

    def set_opacity(self):
        self.submodel.opacity = self.obj.t3d_properties.opacity

        if self.material and self.obj.t3d_properties.opacity_source == "MATERIAL":
            wrapper = MaterialWrapper(self.material)

            if wrapper.get_diffusemap() is not None:
                self.submodel.opacity = wrapper.get_opacity()

    def set_map(self, embed_skins=False, use_generated_img_name=False):
        is_replacable = self.obj.t3d_properties.replacableskin_id != "None"

        if self.material and use_generated_img_name:
            wrapper = MaterialWrapper(self.material)
            diffusemap = wrapper.get_diffusemap()

            if diffusemap and diffusemap.source == 'GENERATED':
                self.submodel.map = diffusemap.name.replace(".", "_")
                return

        if is_replacable and not embed_skins:
            self.submodel.map = self.obj.t3d_properties.replacableskin_id
            return

        self.submodel.map = get_shortpath_from_material(self.material)

    def set_geometry(self, apply_modifiers):
        
        self.submodel.geometry.to_indexed()
            
        context = MikkContext()

        meshes = self.get_meshes(apply_modifiers)

        for (mesh_obj, mesh, local_transform) in meshes:
            
            flip_normals = local_transform.determinant() < 0
                
            for triangle in mesh.loop_triangles:
                    
                for vi in (reversed(range(3)) if flip_normals else range(3)):
                    loop_index = triangle.loops[vi]
                    loop = mesh.loops[loop_index]
                    co = tuple(local_transform @ mesh.vertices[loop.vertex_index].co)
                    normal = tuple(local_transform.to_3x3() @ loop.normal)
                    uv = tuple(mesh.uv_layers.active.data[loop_index].uv)
                    
                    context.addVertex(co, normal, uv)

        for (obj, mesh, transform) in meshes:
            bpy.data.meshes.remove(mesh)
            
        context.calculate()
        (vertices, indices) = context.computeVertexTable()

        self.submodel.geometry.indices = indices
            
        for vert_data in vertices:
            self.submodel.geometry.vertices.new(vert_data)


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
        self.submodel.far_decay_radius = self.obj.data.distance

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