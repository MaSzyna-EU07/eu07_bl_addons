import bpy
import os

LIB_NAME = "eu07_preset_lib.blend"

BSDF_NODE_NAME = "[EU07] Common BSDF"
TEXTURETRAITS_NODE_NAME = "[EU07] Texture Traits"

NODE_GROUPS = (
    BSDF_NODE_NAME,
    TEXTURETRAITS_NODE_NAME
)

@bpy.app.handlers.persistent
def load_presets(filename):
    script_file = os.path.realpath(__file__)
    directory = os.path.dirname(script_file)
    lib_path = os.path.join(directory, LIB_NAME)

    with bpy.data.libraries.load(lib_path, link=True) as (data_from, data_to):
        data_to.node_groups = [
            ng for ng in NODE_GROUPS if ng not in bpy.data.node_groups
        ]


def register():
    bpy.app.handlers.load_post.append(load_presets)


def unregister():
    bpy.app.handlers.load_post.remove(load_presets)