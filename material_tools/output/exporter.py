import eu07_tools

from material_tools.structures import matblock as matblock_mod

class MaterialExporter:
    def __init__(self):
        pass

    def export_to_file(self, file, material):
        if not material.eu07_material.is_mat:
            return

        matblock = material.eu07_material.mat_root
        mapping = self.matblock_to_mapping(matblock)

        eu07_tools.mat.dump(mapping, file)

    def matblock_to_mapping(self, matblock):
        mapping = eu07_tools.mat.create_material()

        if matblock.shader_name:
            mapping["shader"] = matblock.shader_name
        mapping["opacity"] = matblock.opacity
        mapping["selfillum"] = matblock.selfillum
        mapping["size"] = list(matblock.size)
        mapping["shadow_rank"] = matblock.shadow_rank

        for i in range(matblock_mod.MAX_TEXTURES_NUM):
            slotname = f"texture{i + 1}"
            entity = matblock.get_from_texture_slot(slotname)

            if entity:
                key = f"texture_{entity.mat_alias}" if entity.mat_alias else slotname

                if entity.texture_type == "TEXTURE":
                    mapping[key] = entity.shortpath
                else:
                    mapping[key] = list(tex.shortpath for tex in entity.iter_textures())

        for param in matblock.iter_shader_params():
            mapping[param.name] = param.get_values_list()

        for key in eu07_tools.mat.NESTED_MAPPING_KEYS:
            subblock = matblock.get_subblock(key)
            if subblock:
                submapping = self.matblock_to_mapping(subblock)
                mapping[key] = submapping

        return mapping

# New material exporter for later use
class NewMaterialExporter:
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

        if matblock.shader_name:
            outmat.shader = matblock.shader_name
        outmat.opacity = matblock.opacity
        outmat.selfillum = matblock.selfillum
        outmat.size = list(matblock.size)
        outmat.shadow_rank = matblock.shadow_rank

        for i in range(matblock_mod.MAX_TEXTURES_NUM):
            slotname = f"texture{i + 1}"
            entity = matblock.get_from_texture_slot(slotname)

            if entity:
                key = f"texture_{entity.mat_alias}" if entity.mat_alias else slotname

                if entity.texture_type == "TEXTURE":
                    outmat.set_texture_path(key, entity.shortpath)
                else:
                    outmat.set_textureset(key, list(tex.shortpath for tex in entity.iter_textures()))

        for param in matblock.iter_shader_params():
            outmat.shader_params[param.name] = param.get_values_list()

        for key in eu07_tools.mat.NESTED_MAPPING_KEYS:
            subblock = matblock.get_subblock(key)
            if subblock:
                submat = self.matblock_to_outmat(subblock)
                outmat.set_variant(key, submat)

        return outmat

