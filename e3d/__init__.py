import collections

import bpy
from bpy.props import (
    StringProperty, EnumProperty, BoolProperty, 
    FloatProperty, IntProperty, FloatVectorProperty
)
from bpy_extras.io_utils import ImportHelper, ExportHelper

from pathlib import Path
import eu07_bl_addons

import eu07_tools

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
    default_ext: EnumProperty(
        name="Default texture extension",
        default=".tga",
        items=[
            (".tga", "TGA", ""),
            (".dds", "DDS", ""),
            (".png", "PNG", ""),
            (".dds", "BMP", "")
        ]
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

        root = eu07_bl_addons.common.get_root(self.filepath)

        asset_searcher = eu07_tools.utils.AssetSearcher(
            root, 
            Path(self.filepath).parent
        )
        asset_searcher.textures.remove_extension(".mat")
        asset_searcher.textures.set_extension_priority(self.default_ext, 1)

        config = Config(self.report, root, skins, asset_searcher, False)

        with open(self.filepath, "rb") as infile:
            e3d = eu07_tools.e3d.load(infile)
            t3d = list(eu07_tools.utils.e3d_to_t3d(e3d))

            collection = bpy.data.collections.new("T3D")
            bpy.context.scene.collection.children.link(collection)
            eu07_bl_addons.t3d.input_builders.import_model(t3d, collection, config)

        return {'FINISHED'}