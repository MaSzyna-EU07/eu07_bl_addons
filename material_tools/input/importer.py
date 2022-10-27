import eu07_tools

from material_tools import utils
from .shaderparser import ShaderParser
from ..layouter import NodeLayouter


class MaterialImporter:
    def __init__(self, asset_searcher):
        self.asset_searcher = asset_searcher
        self.do_mat_lookup = False
        self.do_name_overwrite = True

    def import_from_shortpath(self, shortpath, bl_material=None):
        abspath = self.asset_searcher.textures.find(shortpath)
        if abspath:
            return self.import_from_abspath(abspath, bl_material, skip_mat_lookup=True)


    def import_from_abspath(self, abspath, bl_material=None, skip_mat_lookup=False):
        shortpath = eu07_tools.utils.shorten_asset_path(abspath)

        if not abspath.endswith(".mat") and self.do_mat_lookup and (not skip_mat_lookup):
            abspath = self.asset_searcher.textures.find(shortpath)

        if bl_material is None:
            bl_material = utils.create_material(shortpath)
        else:
            if self.do_name_overwrite:
                bl_material.name = shortpath

        eu07_material = bl_material.eu07_material
        eu07_material.reset()

        visual_texture = None

        if abspath.endswith(".mat"):
            self.asset_searcher.textures.remove_extension(".mat")
            eu07_material.is_mat = True
            eu07_material.mat_source_path = shortpath

            with open(abspath, encoding="latin-1") as matfile:
                mapping = eu07_tools.mat.load(matfile)
                matblock = self._import_matblock(mapping, eu07_material)

            self.asset_searcher.textures.add_extension(".mat")

            visual_texture = eu07_material.mat_root.get_from_texture_slot("texture1")

        else:
            visual_texture = eu07_material.create_texture()
            visual_texture.set_image_from_abspath(abspath)

        NodeLayouter(bl_material).layout_nodes()
        eu07_material.set_active_color_texture(visual_texture)

        eu07_material.configure()

        return bl_material

    def _import_matblock(self, mapping, eu07_material):
        matblock = eu07_material.create_matblock()

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
                param = matblock.add_shader_param()
                param.name = key
                param.set_values_list(mapping[key])

            elif key in eu07_tools.mat.NESTED_MAPPING_KEYS:
                subblock = self._import_matblock(value, eu07_material)
                matblock.set_subblock(subblock, key)

            elif key.startswith("texture"):
                tex_counter += 1

                if value.use_set:
                    entity = eu07_material.create_randomtextureset()
                    texset = value.set

                    for tex_path in texset:
                        texture = eu07_material.create_texture()
                        self._init_texture_from_shortpath(texture, tex_path)
                        entity.append_texture(texture)
                else:
                    entity = eu07_material.create_texture()
                    self._init_texture_from_shortpath(entity, value.path)

                slot_name = key
                alias = ""
                if "_" in key:
                    _, alias = key.split("_")
                    entity.mat_alias = alias

                if alias and shader_data:
                    slot_name = self._get_slot_name_for_alias(alias, shader_data)
                    if not slot_name:
                        slot_name = f"texture{tex_counter}"

                matblock.set_to_texture_slot(entity, slot_name)

        return matblock

    def _init_texture_from_shortpath(self, texture, shortpath):
        abspath = self.asset_searcher.textures.find(shortpath)
        texture.set_image_from_abspath(abspath)

    def _get_slot_name_for_alias(self, alias, shader_data):
        id_ = shader_data.alias_map.get(alias)

        if id_:
            return f"texture{id_}"












