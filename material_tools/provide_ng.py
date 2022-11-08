import os
import pathlib

import bpy

import material_tools.nodegroups.randomtextureset
from common import get_environment_path
from eu07_tools.utils import AssetSearcher
from .nodegroups.shader_generator import ShaderNodeGroupGenerator


def provide_mat_nodes():
    material_tools.nodegroups.randomtextureset.generate()

    env_path = get_environment_path()
    shaders_dir = pathlib.Path(env_path, "shaders")

    searcher = AssetSearcher(env_path)
    ng_builder = ShaderNodeGroupGenerator(searcher)

    for entry in shaders_dir.iterdir():
        if entry.is_file() and entry.name.startswith("mat_"):
            ng = ng_builder.generate_from_filename(entry.with_suffix("").name)


class EU07_OT_ProvideMATNodeGroups(bpy.types.Operator):
    bl_label = "Provide MAT Nodes"
    bl_idname = "eu07.provide_mat_nodes"

    def execute(self, context):
        provide_mat_nodes()

        return {'FINISHED'}


classes = (
    EU07_OT_ProvideMATNodeGroups,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)