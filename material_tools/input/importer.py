import eu07_tools

from material_tools import utils
from .shaderparser import ShaderParser


class MaterialImporter:
    def __init__(self, asset_searcher):
        self.asset_searcher = asset_searcher
        self.do_mat_lookup = False

    def import_from_shortpath(self, shortpath, material=None):
        abspath = self.asset_searcher.textures.find(shortpath)
        if abspath:
            return self.import_from_abspath(abspath, material, skip_mat_lookup=True)


    def import_from_abspath(self, abspath, material=None, skip_mat_lookup=False):
        shortpath = eu07_tools.utils.shorten_asset_path(abspath)

        if not abspath.endswith(".mat") and self.do_mat_lookup and (not skip_mat_lookup):
            abspath = self.asset_searcher.textures.find(shortpath)

        if material is None:
            material = utils.create_material(shortpath)

        if abspath.endswith(".mat"):
            self.asset_searcher.textures.remove_extension(".mat")
            material.is_mat = True
            material.mat_source_path = shortpath

            with open(abspath, encoding="latin-1") as matfile:
                mapping = eu07_tools.mat.load(matfile)
                matblock = self._import_matblock(mapping, material)

            self.asset_searcher.textures.add_extension(".mat")

            diffuse = material.mat_root.get_from_texture_slot("texture1")
            if diffuse:
                material.set_active_color_texture(diffuse)

        else:
            texture = material.create_texture()
            texture.set_image_from_abspath(abspath)
            material.set_active_color_texture(texture)

        material.configure()

        return material

    def _import_matblock(self, mapping, material):
        matblock = material.create_matblock()

        shader_params = {}
        shader_data = None
        tex_counter = 0

        num_textures = len([k for k in mapping.keys() if k.startswith("texture")])
        use_default_shader = ("shader" not in mapping.keys())

        shader_name = f"default_{num_textures}" if use_default_shader else mapping["shader"]

        shaderparser = ShaderParser(self.asset_searcher)
        self.asset_searcher.shaders.remove_extension(".vert")

        abspath = self.asset_searcher.shaders.find("mat_" + shader_name)

        self.asset_searcher.shaders.add_extension(".vert")

        if abspath:
            shader_data = shaderparser.parse_from_abspath(abspath)

        for key, value in mapping.items():
            if key == "shader":
                matblock.shader_name = value

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
                matblock.set_subblock(subblock, key)

            elif key.startswith("texture"):
                tex_counter += 1

                if value.value_type == "TEXTURE_SET":
                    entity = material.create_randomtextureset()
                    texset = value.value

                    for tex_path in texset:
                        texture = material.create_texture()
                        self._init_texture_from_shortpath(texture, tex_path)
                        entity.append_texture(texture)
                else:
                    entity = material.create_texture()
                    self._init_texture_from_shortpath(entity, value.value)

                slot_name = key
                if "_" in key:
                    _, alias = key.split("_")
                    entity.mat_alias = alias

                if shader_data:
                    slot_name = self._get_slot_name_for_alias(alias, shader_data)
                    if not slot_name:
                        slot_name = f"texture{tex_counter}"

                matblock.set_to_texture_slot(entity, slot_name)

        matblock.shader_params = ";".join((
            f"{k}:{v}"
            for k, v in shader_params.items()
        ))

        return matblock

    def _init_texture_from_shortpath(self, texture, shortpath):
        abspath = self.asset_searcher.textures.find(shortpath)
        texture.set_image_from_abspath(abspath)

    def _get_slot_name_for_alias(self, alias, shader_data):
        id_ = shader_data.alias_map.get(alias)

        if id_:
            return f"texture{id_}"












