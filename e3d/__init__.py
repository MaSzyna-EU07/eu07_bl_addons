import collections
from pathlib import Path

import bpy
from ..common import get_root
import eu07_tools
from ..t3d import input_builders as t3d_input_builders
from bpy.props import (BoolProperty, EnumProperty, FloatProperty,
                       FloatVectorProperty, IntProperty, StringProperty)
from bpy_extras.io_utils import ExportHelper, ImportHelper


class E3DImport(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.e3d"
    bl_label = "Import E3D"
    filename_ext = ".e3d"

    filter_glob: StringProperty(
        default="*.e3d",
        options={'HIDDEN'}
    )
    skin_1: StringProperty(
        name="Skin #1",
    )
    skin_2: StringProperty(
        name="Skin #2",
    )
    skin_3: StringProperty(
        name="Skin #3",
    )
    skin_4: StringProperty(
        name="Skin #4",
    )
    allow_duplicated_materials: BoolProperty(
        name="Duplicate materials",
        default=False
    )

    def execute(self, context):
        Config = collections.namedtuple("Config", "report_func root skins asset_searcher load_includes allow_duplicated_materials")

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

        config = Config(self.report, root, skins, asset_searcher, False, self.allow_duplicated_materials)

        with open(self.filepath, "rb") as infile:
            e3d = eu07_tools.e3d.load(infile)
            t3d = list(eu07_tools.utils.e3d_to_t3d(e3d))

            collection = bpy.context.scene.collection
            t3d_input_builders.import_model(t3d, collection, config)

        return {'FINISHED'}
