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

    def import_from_relpath(self, relpath, traits="", material=None):
        abspath = self.asset_searcher.textures.find(relpath)
        if abspath:
            return self.import_from_abspath(abspath, traits, material)

        return None

    def import_from_abspath(self, abspath, traits="", material=None):
        name = utils.get_qualified_material_name(abspath)
        source_path = common.get_source_path(abspath)

        if material is None:
            material = bpy.data.materials.new(name)
        else:
            material.name = name

        wrapper = MaterialWrapper(material)
        wrapper.initialize()
        wrapper.set_traits_from_string(traits)

        material.eu07_properties.source_path = source_path
        material.eu07_properties.is_imported = True

        if abspath.endswith(".mat"):
            # TODO: Ugly, opacity should be muted without returning
            self._build_from_mat_file(abspath, wrapper)
        else:
            image = bpy.data.images.load(abspath, check_existing=True)
            wrapper.set_diffusemap(image)

        return material

    def _build_from_mat_file(self, abspath, wrapper):
        self.asset_searcher.textures.remove_extension(".mat")

        with open(abspath, encoding="latin-1") as matfile:
            mapping = eu07_tools.mat.load(matfile)


        for key, value in mapping.items():
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

                    wrapper.set_image_has_alpha(self._image_has_alpha(image))

            if key == "opacity":
                wrapper.set_alpha_threshold(value)

        self.asset_searcher.textures.add_extension(".mat")

    def _image_has_alpha(self, img):
        b = 32 if img.is_float else 8
        return (
            img.depth == 2*b or   # Grayscale+Alpha
            img.depth == 4*b      # RGB+Alpha
        )









