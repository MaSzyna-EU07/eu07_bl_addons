from pathlib import Path

import bpy
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper
import eu07_tools.scn
from eu07_tools.utils import AssetSearcher, find_root

from .input_builders import SceneryBuilder

class SCNImport(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.scn"
    bl_label = "Import SCN"

    filter_glob: StringProperty(
        default="*.scn;*.scm;*.inc",
        options={'HIDDEN'}
    )

    def execute(self, context):
        root = find_root(self.filepath)

        asset_searcher = AssetSearcher(root, Path(self.filepath).parent)
        asset_searcher.textures_finder.remove_extension(".mat")

        config = {
            "asset_searcher": asset_searcher
        }

        scn_input = eu07_tools.scn.load(open(self.filepath, encoding='latin-1'))

        builder = SceneryBuilder(config)
        builder.run(scn_input)

        del builder
        
        return {'FINISHED'}

