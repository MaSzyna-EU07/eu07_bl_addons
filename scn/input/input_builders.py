import math

import bpy
import mathutils
import eu07_tools

from scn.decorations import DecorationsBuilder
from scn.trajectory_tools.trajectory_builder import TrajectoryBuilder
from scn.terrain_builder import TerrainBuilder
from scn import trajectory_tools
from scn.sectorizer import Sectorizer
from scn import tree_utils
from mat import HelperMATImporter
from scn import camera

class SceneryBuilder:
    def __init__(self, config):
        self._config = config
        self._trajectory_builder = TrajectoryBuilder()
        self._terrain_builder = TerrainBuilder(config)
        self._decoration_builder = DecorationsBuilder(config)



    def run(self, data):
        for element in data:

            if element.type == "camera":
                camera.create_camera_from_element(element)

            if element.type == "include":
                if element.path.endswith(".scm"):
                    sb = SceneryBuilder(self._config)

                    assearch = self._config["asset_searcher"]

                    abspath = assearch.scenes.find(element.path)

                    with open(abspath, encoding='latin-1') as infile:
                        scn_input = eu07_tools.scn.load(infile)
                        sb.run(scn_input)

                for tree_inc_name in tree_utils.inc_names:
                    if tree_inc_name in element.path.lower():
                        tree_instance = tree_utils.instantiate_tree()

                        height = float(element.parameters[5])
                        breadth = float(element.parameters[6])
                        tree_utils.set_tree_size(tree_instance, height, breadth)

                        tree_instance.location = eu07_tools.utils.swizzle_coords([float(x) for x in element.parameters[1:4]])
                        tree_instance.rotation_euler[2] = math.radians(float(element.parameters[4]))

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
                    profile = trajectory_tools.create_profile_instance(
                        element.subtype, element.geometry_params, element.width, 6 # TODO: Get size from mat, then from track
                    )

                    Sectorizer.auto_put(trajectory)
                    trajectory_tools.set_profile_instance(trajectory, profile)

                    trajectory_tools.set_material(trajectory, HelperMATImporter.import_material_from_relpath(element.map1), 0)
                    trajectory_tools.set_material(trajectory, HelperMATImporter.import_material_from_relpath(element.map2), 1)

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
                    trajectory_side = trajectory_tools.get_switch_side(trajectory_straight)
                    print(trajectory_straight.name)
                    for i in range(4):
                        part_trajectory = trajectory_straight if i < 1 else trajectory_side

                        point_index = i - 1 if i > 1 else i + 1
                        print(point_index)

                        neighbour = trajectory_tools.get_neighbour(part_trajectory, point_index)
                        if neighbour is not None:
                            print("found neighbour")
                            ballast_mat = trajectory_tools.get_material(neighbour, 1)
                            trajectory_tools.copy_profile_instance(neighbour, trajectory_straight)
                            trajectory_tools.copy_profile_instance(neighbour, trajectory_side)

                            trajectory_tools.set_material(trajectory_straight, ballast_mat, 1)
                            trajectory_tools.set_material(trajectory_side, ballast_mat, 1)
                            break