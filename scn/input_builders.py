from pathlib import Path
import cProfile, pstats
from pstats import SortKey

import bpy
from bpy.props import StringProperty, BoolProperty, IntProperty
from bpy_extras.io_utils import ImportHelper


from eu07_tools.utils import AssetSearcher
import eu07_tools

from ..common import get_root
from .decorations import DecorationsBuilder
from .trajectory_builder import TrajectoryBuilder
from .terrain_builder import TerrainBuilder
from . import trajectory_utils
from .sectorizer import Sectorizer
from . import tree_utils
from ..mat import HelperMATImporter

class SCNImport(bpy.types.Operator, ImportHelper):
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

class SceneryBuilder:
    def __init__(self, config):
        self._config = config
        self._trajectory_builder = TrajectoryBuilder()
        self._terrain_builder = TerrainBuilder(config)
        self._decoration_builder = DecorationsBuilder(config)
        self._trees_checklist = [
            "ljtree.inc",
            "ljtreebig.inc",
            "ljtreesmall.inc",
            "tree.inc",
            "treebig.inc",
            "treesmall.inc"
        ]


    def run(self, data):
        for element in data:
            if element.type == "include":
                if element.path.endswith(".scm"):
                    sb = SceneryBuilder(self._config)

                    assearch = self._config["asset_searcher"]

                    abspath = assearch.scenes.find(element.path)

                    with open(abspath, encoding='latin-1') as infile:
                        scn_input = eu07_tools.scn.load(infile)
                        sb.run(scn_input)

                for tree_inc_name in self._trees_checklist:
                    if tree_inc_name in element.path.lower():
                        tree_instance = tree_utils.instantiate_tree()

                        height = float(element.parameters[5])
                        breadth = float(element.parameters[6])
                        tree_utils.set_tree_size(tree_instance, height, breadth)

                        tree_instance.location = eu07_tools.utils.swizzle_coords([float(x) for x in element.parameters[1:4]])
                        tree_instance.rotation_euler[2] = float(element.parameters[4])

                        material = HelperMATImporter.import_material_from_relpath(element.parameters[0])
                        tree_utils.set_tree_material(tree_instance, material)

                        Sectorizer.auto_put(tree_instance)
                        break

            if element.type == "node:triangles":
                self._terrain_builder.add_triangle(element)

            # temporary disabled
            if element.type == "node:track":
                if element.subtype in "normal road river":
                    trajectory = self._trajectory_builder.build_trajectory(element)
                    self._trajectory_builder.create_spline(trajectory, element.p1, element.cv1, element.p2, element.cv2)
                    profile = trajectory_utils.create_profile_instance(
                        element.subtype, element.geometry_params, element.width, 6 # TODO: Get size from mat, then from track
                    )

                    Sectorizer.auto_put(trajectory)
                    trajectory_utils.set_profile_instance(trajectory, profile)

                    trajectory_utils.set_material(trajectory, HelperMATImporter.import_material_from_relpath(element.map1), 0)
                    trajectory_utils.set_material(trajectory, HelperMATImporter.import_material_from_relpath(element.map2), 1)

                elif element.subtype in "switch":
                    trajectory_straight = self._trajectory_builder.build_trajectory(element)
                    self._trajectory_builder.create_spline(trajectory_straight, element.p1, element.cv1, element.p2, element.cv2)
                    trajectory_side = self._trajectory_builder.build_trajectory(element)
                    self._trajectory_builder.create_spline(trajectory_side, element.p3, element.cv3, element.p4, element.cv4)

                    Sectorizer.auto_put(trajectory_straight)
                    Sectorizer.auto_put(trajectory_side)

                    trajectory_side.parent = trajectory_straight
                    trajectory_side.location = (0, 0, 0)

            # elif element.type == "include" and element.path.endswith(".inc"):
            #     inc = bpy.data.objects.new("include", None)
            #     mesh = bpy.data.meshes.new("include")
            #
            #     asset_searcher = AssetSearcher(get_root())
            #     inc_path = asset_searcher.includes.find(inc.path)
            #
            #     with open(inc_path, encoding='latin-1') as incfile:
            #         for entry in eu07_tools.scn.load(incfile, element.parameters)
            #
            #         inc.location = eu07_tools.utils.switch_coordinate_system([float(p) for p in element.parameters[1:4]])
            #         sector = sector_utils.get_sector_by_location(inc.location)
            #
            #     sector_utils.insert_into_sector(inc, sector)

        self.init_switches()
        self._terrain_builder.finish()


    def init_switches(self):
        for o in bpy.data.objects:
            if o.type == 'CURVE':
                trajectory = o
                if trajectory.scn_properties.type_ == "node:track:switch" and trajectory.parent is None:
                    trajectory_straight = trajectory
                    trajectory_side = trajectory_utils.get_switch_side(trajectory_straight)
                    print(trajectory_straight.name)
                    for i in range(4):
                        part_trajectory = trajectory_straight if i < 1 else trajectory_side

                        point_index = i - 1 if i > 1 else i + 1
                        print(point_index)

                        neighbour = trajectory_utils.get_neighbour(part_trajectory, point_index)
                        if neighbour is not None:
                            print("found neighbour")
                            ballast_mat = trajectory_utils.get_material(neighbour, 1)
                            trajectory_utils.copy_profile_instance(neighbour, trajectory_straight)
                            trajectory_utils.copy_profile_instance(neighbour, trajectory_side)

                            trajectory_utils.set_material(trajectory_straight, ballast_mat, 1)
                            trajectory_utils.set_material(trajectory_side, ballast_mat, 1)
                            break