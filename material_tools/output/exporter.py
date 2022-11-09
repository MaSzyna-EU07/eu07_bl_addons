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
        outmat = eu07_tools.mat.create_material()

        if matblock.shader_name != "":
            outmat.shader = matblock.shader_name
        outmat.opacity = matblock.opacity
        outmat.selfillum = matblock.selfillum
        outmat.size = list(matblock.size)
        outmat.shadow_rank = matblock.shadow_rank

        for i in range(matblock_mod.MAX_TEXTURES_NUM):
            slotname = f"texture{i + 1}"
            entity = matblock.get_texture(slotname)

            if entity:
                key = f"texture_{entity.mat_alias}" if entity.mat_alias else slotname

                if entity.texture_type == "TEXTURE":
                    outmat.set_texture_path(key, entity.shortpath_with_traits)
                else:
                    outmat.set_textureset(key, list(tex.shortpath_with_traits for tex in entity.iter_textures()))

        for param in matblock.iter_shader_params():
            outmat.shader_params[param.name] = param.get_values_list()

        for key in eu07_tools.mat.NESTED_MAPPING_KEYS:
            subblock = matblock.get_variant(key)
            if subblock:
                submat = self.matblock_to_outmat(subblock)
                outmat.set_variant(submat, key)

        return outmat

