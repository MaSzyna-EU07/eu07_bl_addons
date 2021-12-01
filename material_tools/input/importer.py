import pathlib

import bpy

import eu07_tools


from material_tools.material_wrapper import MaterialWrapper
from material_tools import utils


class MATImporter:
    def __init__(self, asset_searcher):
        self.use_fake_user = False
        self.asset_searcher = asset_searcher
        self.material = None
        self.allow_duplicates = False

    def import_from_relpath(self, relpath, material=None):
        abspath = self.asset_searcher.textures.find(relpath)
        if abspath:
            return self.import_from_abspath(abspath, material)

        return None

    def import_from_abspath(self, abspath, material=None):
        name = utils.get_qualified_material_name(abspath)

        if abspath.endswith(".mat"):
            with open(abspath, encoding="latin-1") as file:
                return self.import_from_file(file, name, material)
        else:
            return self._import_from_image_abspath(abspath, name, material)

            return self.import_from_mapping(mapping, name, material)

    def _import_from_image_abspath(self, abspath, name, material=None):
        existing = bpy.data.materials.get(name)
        if existing:
            return existing

        if material:
            material.name = name

        self.material = material or bpy.data.materials.new(name)
        self.material.use_backface_culling = True
        self.material.blend_method = 'CLIP'
        self.material.use_nodes = True

        image_node = self.material.node_tree.nodes.new("ShaderNodeTexImage")
        image_node.image = bpy.data.images.load(abspath, check_existing=True)
        utils.ensure_correct_image_node_settings(image_node)

        bsdf = self.material.node_tree.nodes.get("Principled BSDF")
        utils.ensure_correct_principled_bsdf_settings(bsdf)

        color_input_socket = bsdf.inputs[0]
        alpha_input_socket = bsdf.inputs[19]

        self.material.node_tree.links.new(
            image_node.outputs[0],
            color_input_socket
        )

        self.material.node_tree.links.new(
            image_node.outputs[1],
            alpha_input_socket
        )

        return self.material


    def import_from_file(self, file, name="Material", material=None):
        mapping = eu07_tools.mat.load(file)

        return self._import_from_mapping(mapping, name, material)

    def _import_from_mapping(self, mapping, name="Material", material=None):
        existing = bpy.data.materials.get(name)
        if existing:
            return existing

        self.material = material or bpy.data.materials.new(name)
        self.material.name = name
        self.material.use_fake_user = self.use_fake_user

        material_wrapper = MaterialWrapper(self.material)
        material_wrapper.do_basic_setup()
        main_block = self._nodify_mapping(mapping, material_wrapper)
        # TODO: Set active based on variants
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

