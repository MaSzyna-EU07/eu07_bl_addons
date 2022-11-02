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
                inmat = eu07_tools.mat.load(matfile)
                matblock = self._import_matblock(inmat, eu07_material)

            self.asset_searcher.textures.add_extension(".mat")

            visual_texture = eu07_material.mat_root.get_from_texture_slot("texture1")

        else:
            visual_texture = eu07_material.create_texture()
            visual_texture.set_image_from_abspath(abspath)

        NodeLayouter(bl_material).layout_nodes()
        eu07_material.set_active_color_texture(visual_texture)

        eu07_material.configure()

        return bl_material

    def _import_matblock(self, inmat, eu07_material):
        matblock = eu07_material.create_matblock()

        shader_data = None

        num_textures = len(list(inmat.iter_texture_lists()))
        use_default_shader = (inmat.shader == "")

        shader_name = f"default_{num_textures}" if use_default_shader else inmat.shader

        shaderparser = ShaderParser(self.asset_searcher)
        self.asset_searcher.shaders.remove_extension(".vert")

        abspath = self.asset_searcher.shaders.find("mat_" + shader_name)

        self.asset_searcher.shaders.add_extension(".vert")

        if abspath:
            shader_data = shaderparser.parse_from_abspath(abspath)

        matblock.shader_name = inmat.shader
        matblock.opacity = inmat.opacity
        matblock.selfillum = inmat.selfillum
        matblock.size_x, matblock.size_y = inmat.size
        matblock.shadow_rank = inmat.shadow_rank

        for param_key, param_val in inmat.shader_params.items():
            param = matblock.add_shader_param()
            param.name = param_key
            param.set_values_list(param_val)

        for variant_name, variant_mat in inmat.iter_variants():
            subblock = self._import_matblock(variant_mat, eu07_material)
            matblock.set_subblock(subblock, variant_name)

        tex_counter = 1
        for texture_key, texture_list in inmat.iter_texture_lists():

            if len(texture_list) == 1:
                entity = eu07_material.create_texture()
                self._init_texture(entity, texture_list[0])
            else:
                entity = eu07_material.create_randomtextureset()

                for texpathobject in texture_list:
                    texture = eu07_material.create_texture()
                    self._init_texture(texture, texpathobject)
                    entity.append_texture(texture)


            # WHAT IF SHADER NOT EXISTS :(
            slot_name = texture_key
            alias = ""
            if "_" in texture_key:
                _, alias = texture_key.split("_")
                entity.mat_alias = alias

            if alias and shader_data:
                slot_name = self._get_slot_name_for_alias(alias, shader_data)
                if not slot_name:
                    slot_name = f"texture{tex_counter}"

            matblock.set_to_texture_slot(entity, slot_name)

            tex_counter += 1

        return matblock

    def _init_texture(self, texture, tpo):
        abspath = self.asset_searcher.textures.find(tpo.path)
        texture.set_image_from_abspath(abspath)

        texture.disable_wrap_s = tpo.disable_wrap_s
        texture.disable_wrap_t = tpo.disable_wrap_t
        texture.use_sharpen = tpo.use_sharpen

    def _get_slot_name_for_alias(self, alias, shader_data):
        id_ = shader_data.alias_map.get(alias)

        if id_:
            return f"texture{id_}"












