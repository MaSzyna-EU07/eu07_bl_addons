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

        eu07_material = bl_material.eu07_material
        eu07_material.clear()
        eu07_material.init()

        if abspath.endswith(".mat"):
            self.asset_searcher.textures.remove_extension(".mat")
            eu07_material.mat_source_path = shortpath

            with open(abspath, encoding="latin-1") as matfile:
                inmat = eu07_tools.mat.load(matfile)

            matblock = self._import_matblock(inmat, eu07_material)
            eu07_material.mat_root = matblock

            self.asset_searcher.textures.add_extension(".mat")

        else:
            texture = eu07_material.create_texture()
            eu07_material.set_single_texture(texture)

        NodeLayouter(bl_material).layout_nodes()

        return bl_material

    def _import_matblock(self, inmat, eu07_material):
        matblock = eu07_material.create_matblock()

        if "shader" not in inmat.keys():
            num_textures = len([k for k in inmat.keys() if k.startswith("texture")])
            inmat["shader"] = f"default_{num_textures}"

        # Shader first! It implicitly sets proper node group.
        matblock.set_by_key("shader", inmat["shader"])
        matblock.hide_slots()

        for key, value in inmat.items():
            if key in VARIANT_KEYS:
                continue

            if key.startswith("texture"):
                if len(value) == 1:
                    tex_entity = eu07_material.create_texture()
                    self._init_from_tpo(tex_entity, value[0])
                else:
                    tex_entity = eu07_material.create_randomtextureset()

                    for texpathobject in value:
                        texture = eu07_material.create_texture()
                        self._init_from_tpo(texture, texpathobject)
                        tex_entity.append_texture(texture)

                matblock.set_by_key(key, tex_entity)
            else:
                matblock.set_by_key(key, value)


        # Variants imports are postponed, to ensure all nodes has been connected
        for key, value in inmat.items():

            if key not in VARIANT_KEYS:
                continue

            # Get parent shader if not specified locally
            if value.get("shader") is None:
                value["shader"] = inmat["shader"]

            subblock = self._import_matblock(value, eu07_material)
            matblock.set_by_key(key, subblock)

        return matblock

    def _init_from_tpo(self, texture, tpo):
        abspath = self.asset_searcher.textures.find(tpo.path)
        if abspath:
            texture.set_image_from_abspath(abspath)
        else:
            texture.placeholder_path = tpo.path

        texture.disable_wrap_s = tpo.disable_wrap_s
        texture.disable_wrap_t = tpo.disable_wrap_t
        texture.use_sharpen = tpo.use_sharpen












