import random

import bpy

import eu07_tools

import common
from material_tools import utils
from material_tools.wrapper import MaterialWrapper


class MaterialImporter:
    def __init__(self, asset_searcher):
        self.use_fake_user = False
        self.asset_searcher = asset_searcher
        self.material = None
        self.allow_duplicates = False

    def import_from_relpath(self, relpath, material=None, opacity=1):
        abspath = self.asset_searcher.textures.find(relpath)
        if abspath:
            return self.import_from_abspath(abspath, material, opacity)

        return None

    def import_from_abspath(self, abspath, material=None, opacity=1):
        name = utils.get_qualified_material_name(abspath, opacity)
        source_path = common.get_source_path(abspath)

        if material is None:
            material = bpy.data.materials.new(name)
        else:
            material.name = name

        wrapper = MaterialWrapper(material)
        wrapper.initialize()
        wrapper.clean()

        material.eu07_properties.source_path = source_path
        material.eu07_properties.is_imported = True

        if abspath.endswith(".mat"):
            # TODO: Ugly, opacity should be muted without returning
            opacity = self._build_from_mat_file(abspath, wrapper, opacity)
        else:
            image = bpy.data.images.load(abspath, check_existing=True)
            wrapper.set_diffusemap(image)

        wrapper.set_opacity(opacity)

        return material

    def _build_from_mat_file(self, abspath, wrapper, opacity):
        self.asset_searcher.textures.remove_extension(".mat")

        with open(abspath, encoding="latin-1") as matfile:
            mapping = eu07_tools.mat.load(matfile)

        for key, value in mapping.items():
            if key == "opacity":
                opacity = value

            if key.startswith("texture"):
                texture_object = value

                tex_relpath = texture_object.value
                if texture_object.value_type == "TEXTURE_SET":
                    tex_relpath = random.choice(texture_object.value)

                image_path = self.asset_searcher.textures.find(tex_relpath)
                if image_path:
                    image = bpy.data.images.load(image_path, check_existing=True)

                    if key in {"texture_diffuse", "texture1"}:
                        wrapper.set_diffusemap(image)

                    elif key in {"texture_normalmap", "texture2"}:
                        wrapper.set_normalmap(image)

        self.asset_searcher.textures.add_extension(".mat")

        return opacity










