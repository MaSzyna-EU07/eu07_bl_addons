import os
import pathlib

import bpy

from . import randomtextureset, texture_wrap_traits, alpha_threshold
import material_tools.nodegroups.texture_wrap_traits
import material_tools.nodegroups.alpha_threshold
from common import get_environment_path
from eu07_tools.utils import AssetSearcher
from material_tools.nodegroups.shader_generator import ShaderNodeGroupGenerator
from material_tools.utils import SHADER_NAME_PREFIX, get_active_material, get_active_material_node


def provide_mat_nodegroups():
    randomtextureset.generate()
    texture_wrap_traits.generate()
    alpha_threshold.generate()

    env_path = get_environment_path()
    shaders_dir = pathlib.Path(env_path, "shaders")

    searcher = AssetSearcher(env_path)
    ng_builder = ShaderNodeGroupGenerator(searcher)

    for entry in shaders_dir.iterdir():
        if entry.is_file() and entry.name.startswith("mat_"):
            ng = ng_builder.generate_from_filename(entry.with_suffix("").name)


def remove_mat_nodegroups():
    for ng in bpy.data.node_groups:
        if ng.name.startswith("[EU07]"):
            bpy.data.node_groups.remove(ng)


class EU07_OT_ProvideMATNodeGroups(bpy.types.Operator):
    bl_label = "Provide MAT Nodes"
    bl_idname = "eu07.provide_mat_nodegroups"

    def execute(self, context):
        provide_mat_nodegroups()

        return {'FINISHED'}


class EU07_OT_RemoveMATNodeGroups(bpy.types.Operator):
    bl_label = "Remove MAT Nodes"
    bl_idname = "eu07.remove_mat_nodegroups"

    def execute(self, context):
        remove_mat_nodegroups()

        return {'FINISHED'}


class EU07_OT_ToggleMATShaderInputs(bpy.types.Operator):
    bl_label = "Disable all inputs"
    bl_idname = "eu07.toggle_shader_inputs"

    hidden_state: bpy.props.BoolProperty(
        default=True
    )

    @classmethod
    def poll(cls, context):
        active_material = get_active_material(context)
        active_node = get_active_material_node(active_material)

        return active_node is not None

    def execute(self, context):
        node = get_active_material_node(get_active_material(context))
        for inp in node.inputs:
            inp.hide = self.hidden_state

        return {'FINISHED'}


classes = (
    EU07_OT_ProvideMATNodeGroups,
    EU07_OT_RemoveMATNodeGroups,
    EU07_OT_ToggleMATShaderInputs
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)