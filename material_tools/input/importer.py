import eu07_tools
from eu07_tools.mat import VARIANT_KEYS

from material_tools import utils
from ..layouter import NodeLayouter
from ..ng_ops import provide_mat_nodegroups


class MaterialImporter:
    def __init__(self, asset_searcher):
        self.asset_searcher = asset_searcher
        self.do_mat_lookup = False
        self.do_name_overwrite = True
        self._eu07_material = None

    def import_from_shortpath(self, shortpath, bl_material=None):
        abspath = self.asset_searcher.textures.find(shortpath)
        if abspath:
            return self.import_from_abspath(abspath, bl_material, skip_mat_lookup=True)


    def import_from_abspath(self, abspath, bl_material=None, skip_mat_lookup=False):
        provide_mat_nodegroups()

        shortpath = eu07_tools.utils.shorten_asset_path(abspath)

        if not abspath.endswith(".mat") and self.do_mat_lookup and (not skip_mat_lookup):
            abspath = self.asset_searcher.textures.find(shortpath)

        if bl_material is None:
            bl_material = utils.create_material(shortpath)
        else:
            if self.do_name_overwrite:
                bl_material.name = shortpath

        self._eu07_material = bl_material.eu07_material
        self._eu07_material.clear()
        self._eu07_material.init()

        if abspath.endswith(".mat"):
            self.asset_searcher.textures.remove_extension(".mat")
            self._eu07_material.mat_source_path = shortpath

            with open(abspath, encoding="latin-1") as matfile:
                inmat = eu07_tools.mat.load(matfile)

            matblock = self._import_matblock(inmat)
            self._eu07_material.mat_root = matblock

            self.asset_searcher.textures.add_extension(".mat")

        else:
            texture = self._eu07_material.create_texture()
            self._eu07_material.set_single_texture(texture)

        NodeLayouter(bl_material).layout_nodes()

        return bl_material

    def _import_matblock(self, inmat):
        matblock = self._eu07_material.create_matblock()

        if "shader" not in inmat.keys():
            inmat["shader"] = inmat.get_default_shader_name()

        # Shader first! It implicitly sets proper node group.
        matblock.set_by_key("shader", inmat["shader"])
        matblock.hide_slots()

        for key, value in inmat.items():
            if key in VARIANT_KEYS:
                continue

            if key.startswith("texture"):
                value = self._import_texture(value)

            matblock.set_by_key(key, value)


        # Variants imports are postponed, to ensure all nodes has been connected
        for key, value in inmat.items():

            if key not in VARIANT_KEYS:
                continue

            # Get parent shader if not specified locally
            if value.get("shader") is None:
                value["shader"] = inmat["shader"]

            subblock = self._import_matblock(value)
            matblock.set_by_key(key, subblock)

        return matblock

    def _import_texture(self, value):
        if value.is_path:
            tex_entity = self._eu07_material.create_texture()
            self._init_from_tpo(tex_entity, value.paths[0])

        elif value.is_randomset:
            tex_entity = self._eu07_material.create_randomtextureset()

            for tpo in value.paths:
                texture = self._eu07_material.create_texture()
                self._init_from_tpo(texture, tpo)
                tex_entity.append_texture(texture)

        return tex_entity

    def _init_from_tpo(self, texture, tpo):
        abspath = self.asset_searcher.textures.find(tpo.path)
        if abspath:
            texture.set_image_from_abspath(abspath)
        else:
            texture.placeholder_path = tpo.path

        texture.disable_wrap_s = tpo.disable_wrap_s
        texture.disable_wrap_t = tpo.disable_wrap_t
        texture.use_sharpen = tpo.use_sharpen












