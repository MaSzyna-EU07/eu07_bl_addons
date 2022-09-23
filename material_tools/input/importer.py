import eu07_tools

from material_tools import utils


class MaterialImporter:
    def __init__(self, asset_searcher):
        self.asset_searcher = asset_searcher
        self.do_mat_lookup = False

    def import_from_shortpath(self, shortpath, material=None):
        abspath = self.asset_searcher.textures.find(shortpath)
        if abspath:
            return self.import_from_abspath(abspath, material, skip_mat_lookup=True)

        return None

    def import_from_abspath(self, abspath, material=None, skip_mat_lookup=False):
        shortpath = eu07_tools.utils.shorten_asset_path(abspath)

        if not abspath.endswith(".mat") and self.do_mat_lookup and (not skip_mat_lookup):
            abspath = self.asset_searcher.textures.find(shortpath)

        if material is None:
            material = utils.create_material(shortpath)

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
                material.set_subblock(subblock, key)

            elif key.startswith("texture"):
                if value.value_type == "TEXTURE_SET":
                    entity = material.create_randomtextureset()
                    texset = value

                    for tex_path in texset:
                        texture = material.create_texture()
                        self._init_texture_from_shortpath(texture, tex_path)
                        entity.append_texture(texture)
                else:
                    entity = material.create_texture()
                    self._init_texture_from_shortpath(entity, value)

                matblock.set_to_texture_slot(entity, key)

        matblock.shader_params = ";".join((
            f"{k}:{v}"
            for k, v in shader_params.items()
        ))

        return matblock

    def _init_texture_from_shortpath(self, texture, shortpath):
        abspath = self.asset_searcher.textures.find(shortpath)
        texture.set_image_from_abspath(abspath)









