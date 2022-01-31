import bpy

import eu07_tools

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

        if material is None:
            material = bpy.data.materials.new(name)

        wrapper = MaterialWrapper(material)
        wrapper.adjust_specularity()

        if abspath.endswith(".mat"):
            # TODO: Ugly, opacity should be muted without returning
            opacity = self._build_from_mat_file(abspath, wrapper, opacity)
        else:
            image = bpy.data.images.load(abspath, check_existing=True)
            wrapper.set_diffuse(image)

        wrapper.set_opacity(opacity)

        return material

    def _build_from_mat_file(self, abspath, wrapper, opacity):
        self.asset_searcher.textures.remove_extension(".mat")

        with open(abspath, encoding="latin-1") as matfile:
            mapping = eu07_tools.mat.load(matfile)

        for key, value in mapping.items():
            if key == "opacity":
                opacity = value # TODO: Test if it works

            if key.startswith("texture"):
                image_path = self.asset_searcher.textures.find(value.path)
                image = bpy.data.images.load(image_path, check_existing=True)

                if key in {"texture_diffuse", "texture1"}:
                    wrapper.set_diffuse(image)

                elif key in {"texture_normalmap", "texture2"}:
                    wrapper.set_normalmap(image)

        self.asset_searcher.textures.add_extension(".mat")

        return opacity








