from pathlib import Path

import bpy
from bpy.props import StringProperty, BoolProperty, IntProperty
from bpy_extras.io_utils import ImportHelper

from ... import eu07_tools
from ...common import get_environment_path
from ...scn.input.input_builders import SceneryBuilder
from ...scn.sectorizer import Sectorizer


class SCNImportOperator(bpy.types.Operator, ImportHelper):
    bl_idname = "eu07.scn_import"
    bl_label = "Import SCN"

    filter_glob: StringProperty(
        default="*.scn;*.scm;*.inc",
        options={'HIDDEN'}
    )

    import_terrain: BoolProperty(
        name="Import Terrain",
        default=True,
        options={'HIDDEN'}
    )

    import_tracks: BoolProperty(
        name="Import Tracks",
        default=True,
        options={'HIDDEN'}
    )

    import_roads: BoolProperty(
        name="Import Roads",
        default=True,
        options={'HIDDEN'}
    )

    import_rivers: BoolProperty(
        name="Import Rivers",
        default=True,
        options={'HIDDEN'}
    )

    inc_recursion_depth: IntProperty(
        name="Include recursion depth",
        default=1,
        options={'HIDDEN'}
    )

    do_weld_terrain: BoolProperty(
        name="Weld Terrain Triangles",
        default=True
    )

    cache_tracks_neighbours: BoolProperty(
        name="Cache Tracks Neibourghs",
        options={'HIDDEN'}
    )

    sector_size: IntProperty(
        name="Sector Size",
        default=2000,
        min=0,
    )

    def execute(self, context):
        root = get_environment_path(self.filepath)

        asset_searcher = eu07_tools.utils.AssetSearcher(
            root, Path(self.filepath).parent
        )

        config = {
            "asset_searcher": asset_searcher,
            "do_weld_terrain": self.do_weld_terrain
        }

        Sectorizer.sector_size = self.sector_size

        with open(self.filepath, encoding='latin-1') as infile:
            scn_input = eu07_tools.scn.load(infile)

            builder = SceneryBuilder(config)
            builder.run(scn_input)

            del builder

        return {'FINISHED'}