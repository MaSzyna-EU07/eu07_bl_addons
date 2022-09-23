import random

import bpy

import eu07_tools

import common
from material_tools import utils


class MaterialImporter:
    def __init__(self):
        self.asset_searcher = None
        self.load_mat_for_texture = False

    def import_from_shortpath(self, shortpath, material=None):
        abspath = self.asset_searcher.textures.find(shortpath)
        if abspath:
            return self.import_from_abspath(abspath, material)

        return None

    def import_from_abspath(self, abspath, material=None):
        if material is None:
            material = utils.create_material()

        if abspath.endswith(".mat"):
            self.asset_searcher.textures.remove_extension(".mat")

            with open(abspath, encoding="latin-1") as matfile:
                mapping = eu07_tools.mat.load(matfile)
                matblock = self._import_matblock(mapping, material)

            self.asset_searcher.textures.add_extension(".mat")
        else:
            texture = material.create_texture()
            texture.set_image_from_abspath(abspath)
            material.set_active_color_texture(texture)

    def _import_matblock(self, mapping, material):
        matblock = material.create_matblock()

        shader_params = {}

        for key, value in mapping.items():
            if key == "shader":
                matblock.shader = value

            elif key == "opacity":
                matblock.opacity = value

            elif key == "selfillum":
                matblock.selfillum = value

            elif key == "size":
                matblock.size_x, matblock.size_y = value

            elif key == "shadow_rank":
                matblock.shadow_rank = value

            elif key.startswith("param"):
                shader_params[key] = value

            elif key in eu07_tools.mat.NESTED_MAPPING_KEYS:
                subblock = self._import_matblock(value, material)
                material.set_subblock(subblock, key)

            elif key.startswith("texture"):
                if value.value_type == "TEXTURE_SET":
                    entity = material.create_randomtextureset()
                    texset = value

                    for tex_path in texset:
                        texture = material.create_texture()
                        self._init_texture_from_shortpath(tex_path)
                        entity.append_texture(texture)
                else:
                    entity = material.create_texture()
                    self._init_texture_from_shortpath(value)

                matblock.set_to_texture_slot(entity, key)

        matblock.shader_params = ";".join((
            f"{k}:{v}"
            for k, v in shader_params.items()
        ))

        return matblock

    def _init_texture_from_shortpath(self, texture, shortpath):
        abspath = self.asset_searcher.textures.find(shortpath)
        texture.set_image_from_abspath(abspath)









