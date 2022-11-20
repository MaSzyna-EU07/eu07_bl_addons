import eu07_tools
from eu07_tools.mat import NESTED_MAPPING_KEYS
from eu07_tools.mat.shaderparser import ShaderParser

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

        if "shader" not in inmat.keys():
            num_textures = len([k for k in inmat.keys() if k.startswith("texture")])
            inmat["shader"] = f"default_{num_textures}"

        matblock.shader = inmat["shader"]
        matblock.hide_slots()

        for key, value in inmat.items():

            if key == "opacity":
                matblock.opacity = inmat["opacity"]

            elif key == "selfillum":
                matblock.selfillum = inmat["selfillum"]

            elif key == "size":
                matblock.size_x, matblock.size_y = inmat["size"]

            elif key == "shadow_rank":
                matblock.shadow_rank = inmat["shadow_rank"]

            elif key.startswith("param"):
                # TODO: Params can be indexed, but this rarely happens
                input_name = key_to_input_name(key, matblock)
                try:
                    matblock.set_param(input_name, value)
                except KeyError as e:
                    # TODO: Make logging?
                    print(e)

            elif key.startswith("texture"):
                if len(value) == 1:
                    entity = eu07_material.create_texture()
                    self._init_from_tpo(entity, value[0])
                else:
                    entity = eu07_material.create_randomtextureset()

                    for texpathobject in value:
                        texture = eu07_material.create_texture()
                        self._init_from_tpo(texture, texpathobject)
                        entity.append_texture(texture)

                input_name = key_to_input_name(key, matblock)
                matblock.set_texture(input_name, entity)


        # Variants import are delayed to ensure proper node connection
        for key, value in inmat.items():

            if key not in NESTED_MAPPING_KEYS:
                continue

            # Get parent shader if not specified locally
            if value.get("shader") is None:
                value["shader"] = inmat["shader"]

            subblock = self._import_matblock(value, eu07_material)
            matblock.set_variant(key, subblock)

        return matblock

    def _init_from_tpo(self, texture, tpo):
        abspath = self.asset_searcher.textures.find(tpo.path)
        texture.set_image_from_abspath(abspath)

        texture.disable_wrap_s = tpo.disable_wrap_s
        texture.disable_wrap_t = tpo.disable_wrap_t
        texture.use_sharpen = tpo.use_sharpen


def key_to_input_name(key, matblock):
    if "_" in key:
        alias_parts = key.split("_")[1:]
        input_name = " ".join(alias_parts).capitalize()
    else:
        unit_index = int(key[-1])
        if key.startswith("texture"):
            input_name = matblock.node_tree.eu07_shader_inputs_map.get_texture_input_name(unit_index)
        # TODO: Same for params

    return input_name












