import pathlib

import bpy

import eu07_tools

from mat.material_wrapper import MaterialWrapper
from common.utils import get_qualified_material_name, get_root


class MATImporter:
    def __init__(self, asset_searcher):
        self.use_fake_user = False
        self.asset_searcher = asset_searcher
        self.material = None

    def import_from_relpath(self, relpath):
        abspath = self.asset_searcher.textures.find(relpath)
        if abspath:
            return self.import_from_abspath(abspath)

        return None

    def import_from_abspath(self, abspath):
        name = get_qualified_material_name(abspath)

        if abspath.endswith(".mat"):
            with open(abspath, encoding="latin-1") as file:
                return self.import_from_file(file, name)
        else:
            mapping = eu07_tools.mat.create_mapping()
            mapping["texture_diffuse"] = str(pathlib.Path(abspath).relative_to(get_root(abspath)))

            return self.import_from_mapping(mapping, name)

    def import_from_file(self, file, name="Material"):
        mapping = eu07_tools.mat.load(file)
        return self.import_from_mapping(mapping, name)

    def import_from_mapping(self, mapping, name="Material"):
        self.material = bpy.data.materials.new(name)
        self.material.use_fake_user = self.use_fake_user

        material_wrapper = MaterialWrapper(self.material)
        material_wrapper.do_basic_setup()
        main_block = self._nodify_mapping(mapping, material_wrapper)
        main_block.make_active()

        return self.material

    def _nodify_mapping(self, mapping, material_wrapper):
        block_wrapper = material_wrapper.create_block()

        shader_params = []

        for key, value in mapping.items():

            if key == "shader":
                block_wrapper.set_shader_name(value)

            elif "param" in key:
                shader_params.append(
                    f"{key}:" + " ".join(str(v) for v in value)
                )

            elif "texture" in key:
                texture_object = value

                self.asset_searcher.textures.remove_extension(".mat")

                if texture_object.value_type == "TEXTURE_PATH":
                    texture_path = self.asset_searcher.textures.find(texture_object.path)
                    image = bpy.data.images.load(texture_path, check_existing=True)

                    texture_index = eu07_tools.mat.get_texture_index_from_key(key)
                    alias = eu07_tools.mat.get_alias_from_key(key)
                    block_wrapper.set_texture_image(image, texture_index, alias)

                elif texture_object.value_type == "TEXTURE_SET":
                    pass

                self.asset_searcher.textures.add_extension(".mat", priority=0)

            elif key == "opacity":
                block_wrapper.set_opacity(value)

            elif key == "selfillum":
                block_wrapper.set_selfillum(value)

            elif key == "size":
                block_wrapper.set_size(value)

            elif key == "shadow_rank":
                block_wrapper.set_shadow_rank(value)

            elif key in eu07_tools.mat.NESTED_MAPPING_KEYS:
                nested_wrapper = self._nodify_mapping(value, material_wrapper)
                block_wrapper.set_sub_block(key, nested_wrapper)

        shader_params_joined = ";".join(shader_params)
        block_wrapper.set_shader_params(shader_params_joined)

        return block_wrapper

