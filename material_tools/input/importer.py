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
        eu07_material.clear()

        if abspath.endswith(".mat"):
            eu07_material.init_mat()
            self.asset_searcher.textures.remove_extension(".mat")
            eu07_material.is_mat = True
            eu07_material.mat_source_path = shortpath

            with open(abspath, encoding="latin-1") as matfile:
                inmat = eu07_tools.mat.load(matfile)
                matblock = self._import_matblock(inmat, eu07_material)
                eu07_material.mat_root = matblock

            self.asset_searcher.textures.add_extension(".mat")

        else:
            eu07_material.init_texture()
            texture = eu07_material.create_texture()
            eu07_material.set_single_texture(texture)

        NodeLayouter(bl_material).layout_nodes()

        return bl_material

    def _import_matblock(self, inmat, eu07_material):
        matblock = eu07_material.create_matblock()

        num_textures = len(list(inmat.iter_texture_lists()))
        use_default_shader = (inmat.shader == "")

        shader_name = f"default_{num_textures}" if use_default_shader else inmat.shader

        matblock.shader = shader_name
        matblock.opacity = inmat.opacity
        matblock.selfillum = inmat.selfillum
        matblock.size_x, matblock.size_y = inmat.size
        matblock.shadow_rank = inmat.shadow_rank

        for param_key, param_val in inmat.shader_params.items():
            matblock.set_param(param_key, param_val)

        for variant_name, variant_mat in inmat.iter_variants():
            subblock = self._import_matblock(variant_mat, eu07_material)
            matblock.set_variant(variant_name, subblock)

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

            matblock.set_texture(texture_key, entity)

            tex_counter += 1

        return matblock

    def _init_texture(self, texture, tpo):
        abspath = self.asset_searcher.textures.find(tpo.path)
        texture.set_image_from_abspath(abspath)

        texture.disable_wrap_s = tpo.disable_wrap_s
        texture.disable_wrap_t = tpo.disable_wrap_t
        texture.use_sharpen = tpo.use_sharpen














