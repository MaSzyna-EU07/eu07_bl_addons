import eu07_tools

from material_tools.structures import matblock as matblock_mod

class MaterialExporter:
    def __init__(self):
        pass

    def export_to_file(self, file, material):
        if not material.eu07_material.is_mat:
            return

        matblock = material.eu07_material.mat_root
        outmat = self.matblock_to_outmat(matblock)

        eu07_tools.mat.dump(outmat, file)

    def matblock_to_outmat(self, matblock):
        outmat = eu07_tools.mat.MATMaterial()

        for key in matblock.iter_used_keys():
            value = matblock.get_by_key(key)

            if key.startswith("texture"):
                tex_entity = value
                if tex_entity.texture_type == "TEXTURE":
                    value = eu07_tools.utils.TexturePath(tex_entity.shortpath_with_traits)
                else:
                    value = list(
                        eu07_tools.utils.TexturePath(tex_entity.shortpath_with_traits)
                        for tex in tex_entity.iter_textures()
                    )

            elif key in eu07_tools.mat.VARIANT_KEYS:
                subblock = value
                if subblock:
                    value = self.matblock_to_outmat(subblock)

            outmat[key] = value

        return outmat

