import collections
from pathlib import Path

import bpy

from common.base_model_importer import BaseModelImporter
from ..common import get_root
import eu07_tools
from ..t3d import input as t3d_input_builders


class E3DImporter(BaseModelImporter):
    bl_idname = "eu07.import_e3d"
    bl_label = "Import E3D"
    filename_ext = ".e3d"

    filter_glob: bpy.props.StringProperty(
        default="*.e3d",
        options={'HIDDEN'}
    )

    def execute(self, context):
        Config = collections.namedtuple("Config", "report_func root skins asset_searcher load_includes")

        skins = {
            "replacableskin": self.skin_1,
            "-1": self.skin_1,
            "-2": self.skin_2,
            "-3": self.skin_3,
            "-4": self.skin_4
        }

        root = get_root(self.filepath)

        asset_searcher = eu07_tools.utils.AssetSearcher(
            root,
            Path(self.filepath).parent
        )

        config = Config(self.report, root, skins, asset_searcher, False)

        with open(self.filepath, "rb") as infile:
            e3d = eu07_tools.e3d.load(infile)
            t3d = list(eu07_tools.utils.e3d_to_t3d(e3d))

            collection = bpy.context.scene.collection
            t3d_input_builders.import_model(t3d, collection, config)

        return {'FINISHED'}


