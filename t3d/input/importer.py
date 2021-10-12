import collections
from pathlib import Path

import bpy
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
import eu07_tools

from common import get_root, join_meshes
from common.base_model_importer import BaseModelImporter
from .input_builders import import_model


class T3DImporter(BaseModelImporter):
    bl_idname = "eu07.import_t3d"
    bl_label = "Import T3D"
    filename_ext = ".t3d"

    filter_glob: StringProperty(
        default="*.t3d",
        options={'HIDDEN'}
    )
    load_includes: BoolProperty(
        name="Load included submodels",
        default=True,
    )

    def execute(self, context):
        Config = collections.namedtuple(
            "Config",
            "report_func root skins asset_searcher load_includes import_meshes import_spots import_stars merge_all"
        )

        skins = self._get_replacableskins()

        root = get_root(self.filepath)

        asset_searcher = eu07_tools.utils.AssetSearcher(
            root,
            Path(self.filepath).parent
        )

        asset_searcher.models.remove_extension(".e3d")

        config = Config(
            self.report, root, skins, asset_searcher,
            self.load_includes, self.import_meshes, self.import_spots, self.import_stars,
            self.merge_all
        )

        collection = bpy.context.scene.collection

        with open(self.filepath, "r", encoding="latin-1") as file:
            elements = eu07_tools.t3d.load(file)
            imported = import_model(elements, config)

            if self.merge_all:
                name = str(Path(self.filepath).with_suffix("").relative_to(root))
                join_meshes(imported, name, bpy.context.scene.collection)

        return {'FINISHED'}