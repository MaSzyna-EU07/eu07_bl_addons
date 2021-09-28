import math
import re

import bpy
import bmesh
import eu07_tools
from bpy_extras import view3d_utils

import preferences
from common import get_path_from_material

inc_names = [
    "ljtree.inc",
    "ljtreebig.inc",
    "ljtreesmall.inc",
    "tree.inc",
    "treebig.inc",
    "treesmall.inc"
]


def instantiate_tree():
    tree_instance = bpy.data.objects.new("Tree", get_tree_template().data)
    tree_instance.material_slots[0].link = 'OBJECT'
    tree_instance.scn_properties.type_ = "tree"

    constraint = tree_instance.constraints.new('LIMIT_ROTATION')
    constraint.use_transform_limit = True
    constraint.use_limit_y = True
    constraint.use_limit_x = True
    constraint.min_y, constraint.max_y = 0, 0
    constraint.min_x, constraint.max_x = 0, 0

    return tree_instance


def get_tree_template():
    tree_template = bpy.data.objects.get("TreeTemplate")

    if not tree_template:
        tree_template = bpy.data.objects.new("TreeTemplate", bpy.data.meshes.new("TreeTemplate"))
        tree_template.data.materials.append(None)
        tree_template.material_slots[0].link = 'OBJECT'


        mesh = bmesh.new()
        uv_layer = mesh.loops.layers.uv.new()

        geometry_data = [
            (1, 1, 0, 0, 0.99),
            (1, 0, 0, 0, 0),
            (-1, 1, 0, 1, 0.99),
            (-1, 0, 0, 1, 0),
            (-1, 1, 0, 1, 0.99),
            (1, 0, 0, 0, 0),
            (1, 0, 0, 0, 0),
            (1, 1, 0, 0, 0.99),
            (-1, 1, 0, 1, 0.99),
            (-1, 1, 0, 1, 0.99),
            (-1, 0, 0, 1, 0),
            (1, 0, 0, 0, 0),
            (0, 0, -1, 0, 0),
            (0, 1, -1, 0, 0.99),
            (0, 1, 1, 1, 0.99),
            (0, 1, 1, 1, 0.99),
            (0, 0, 1, 1, 0),
            (0, 0, -1, 0, 0),
            (0, 1, -1, 0, 0.99),
            (0, 0, -1, 0, 0),
            (0, 1, 1, 1, 0.99),
            (0, 0, 1, 1, 0),
            (0, 1, 1, 1, 0.99),
            (0, 0, -1, 0, 0)
        ]


        for i in range(len(geometry_data) // 3):
            vertex_index_start = i * 3
            vertex_index_end = vertex_index_start + 3

            face_verts_data = geometry_data[vertex_index_start:vertex_index_end]

            face_verts_coords = [eu07_tools.utils.swizzle_coords(vertex_data[:3]) for vertex_data in face_verts_data]

            face_verts = [mesh.verts.new(coords) for coords in face_verts_coords]
            face = mesh.faces.new(face_verts)

            for vertex_index, loop in enumerate(face.loops):
                loop[uv_layer].uv = face_verts_data[vertex_index][3:]

            if i % 2 == 0:
                face.normal_flip()

        mesh.to_mesh(tree_template.data)
        mesh.free()

        collection = bpy.data.collections.get("Templates") or bpy.data.collections.new("Templates")
        collection.objects.link(tree_template)

    return tree_template


def set_tree_size(tree_instance, height, breadth):
    tree_instance.scale.x = breadth
    tree_instance.scale.y = breadth
    tree_instance.scale.z = height


def get_tree_size(tree_instance):
    return (tree_instance.scale.z, tree_instance.scale.y)


def set_tree_material(tree_instance, material):
    tree_instance.material_slots[0].material = material

def filter_trees_materials(regex):
    for mat in bpy.data.materials:
        if re.search(regex, mat.name):
            yield mat


def create_tree_include(tree_object):
    tree_inc = eu07_tools.scn.create_element("include")
    tree_inc.path = "tree.inc"
    tree_inc.parameters.append(get_path_from_material(tree_object.active_material))
    tree_inc.parameters.extend(eu07_tools.utils.swizzle_coords(tree_object.location))
    tree_inc.parameters.append(math.degrees(tree_object.rotation_euler[2]))
    tree_inc.parameters.extend(get_tree_size(tree_object))

    tree_inc.parameters = [str(p) for p in tree_inc.parameters]

    return tree_inc


class AddTreeOperator(bpy.types.Operator):
    bl_idname = "eu07.add_tree"
    bl_label = "Add Tree"

    def execute(self, context):
        self.tree_instance.location = self.snapped_loc
        bpy.ops.object.select_all(action='DESELECT')
        self.tree_instance.select_set(True)
        return {'FINISHED'}

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':  # Apply
            region = context.region
            region_data = context.space_data.region_3d
            self.mouse_pos = event.mouse_region_x, event.mouse_region_y

            origin = view3d_utils.region_2d_to_origin_3d(region, region_data, self.mouse_pos)
            direction = view3d_utils.region_2d_to_vector_3d(region, region_data, self.mouse_pos)

            depsgraph = bpy.context.evaluated_depsgraph_get()

            obj = self.tree_instance
            while True:
                hit, origin, normal, index, obj, matrix = \
                    context.scene.ray_cast(depsgraph, origin + direction * 0.0001, direction)
                if hit and obj is not self.tree_instance:
                    self.snapped_loc = origin
                    break

            self.execute(context)
        elif event.type == 'LEFTMOUSE':
            return {'FINISHED'}
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.context.scene.collection.objects.unlink(self.tree_instance)
            bpy.data.objects.remove(self.tree_instance)
            return {'CANCELLED'}
        elif event.type == 'WHEELUPMOUSE':
            self.material_select_index += 1
            if self.material_select_index > len(self.materials) - 1:
                self.material_select_index = 0
        elif event.type == 'WHEELDOWNMOUSE':
            self.material_select_index -= 1
            if self.material_select_index < 0:
                self.material_select_index = len(self.materials) - 1

        self.tree_instance.material_slots[0].material = self.materials[self.material_select_index]

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.snapped_loc = context.scene.cursor.location
        self.materials = list(filter_trees_materials(r'{}'.format(preferences.get_preferences().trees_material_regex)))
        self.tree_instance = instantiate_tree()
        self.material_select_index = 0
        self.tree_instance.scale = (3, 3, 7)
        context.scene.collection.objects.link(self.tree_instance)
        self.mouse_pos = event.mouse_region_x, event.mouse_region_y
        self.execute(context)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}





