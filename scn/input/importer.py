from pathlib import Path
import cProfile
import pstats
from pstats import SortKey

import bpy
from bpy.props import StringProperty, BoolProperty, IntProperty
from bpy_extras.io_utils import ImportHelper
import eu07_tools

from ..sectorizer import Sectorizer
from common import get_root
from .input_builders import SceneryBuilder

class SCNImporter(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.scn"
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
        root = get_root(self.filepath)

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
            with cProfile.Profile() as pr:
                builder.run(scn_input)

            sortby = SortKey.TIME
            ps = pstats.Stats(pr).sort_stats(sortby)
            ps.print_stats()

        del builder

        return {'FINISHED'}