import math
import pathlib

import bpy
import mathutils
import eu07_tools
import scn.trajectory_tools.profile

from scn.decorations import DecorationsBuilder
from scn.trajectory_tools.trajectory_builder import TrajectoryBuilder
from scn.terrain import TerrainBuilder
from scn import trajectory_tools
from scn.sectorizer import Sectorizer
from mat import HelperMATImporter
from common import includes
import scn

class SceneryBuilder:
    def __init__(self, config, include_identifier=-1):
        self._config = config
        self._trajectory_builder = TrajectoryBuilder()
        self._terrain_builder = TerrainBuilder(config)
        self._decoration_builder = DecorationsBuilder(config)
        self._include_identifier = include_identifier

    def run(self, data):
        for element in data:
            obj = None
            if element.type == "camera":
                obj = scn.camera.create_camera_from_element(element)

            if element.type == "node:memcell":
                obj = scn.memcell.create_memcell_from_element(element)

            if element.type == "include":
                if element.path.endswith(".scm"):
                    include = includes.add_include()

                    filepath = pathlib.Path("scenery", element.path)
                    include.name = filepath.stem
                    include.file_path = str(filepath)

                    sb = SceneryBuilder(self._config, include.identifier)

                    assearch = self._config["asset_searcher"]

                    abspath = assearch.scenes.find(element.path)

                    with open(abspath, encoding='latin-1') as infile:
                        scn_input = eu07_tools.scn.load(infile)
                        sb.run(scn_input)

                for tree_inc_name in scn.tree_utils.inc_names:
                    if tree_inc_name in element.path.lower():
                        tree_instance = scn.tree_utils.instantiate_tree()

                        height = float(element.parameters[5])
                        breadth = float(element.parameters[6])
                        scn.tree_utils.set_tree_size(tree_instance, height, breadth)

                        tree_instance.location = eu07_tools.utils.swizzle_coords([float(x) for x in element.parameters[1:4]])
                        tree_instance.rotation_euler[2] = math.radians(float(element.parameters[4]))

                        material = HelperMATImporter.import_material_from_relpath(element.parameters[0])
                        scn.tree_utils.set_tree_material(tree_instance, material)

                        Sectorizer.auto_put(tree_instance)
                        tree_instance.eu07_include_identifier = self._include_identifier
                        break

            if element.type == "node:triangles":
                self._terrain_builder.add_triangle(element)

            if element.type == "node:sound":
                obj = scn.sound.create_sound_from_element(element)

            if element.type == "node:track":
                if element.subtype in "normal road river":
                    trajectory = self._trajectory_builder.build_trajectory(element)
                    self._trajectory_builder.create_spline(trajectory, element.p1, element.cv1, element.p2, element.cv2, element.p1_roll, element.p2_roll)
                    profile = scn.trajectory_tools.profile.create_instance(
                        element.subtype, element.geometry_params, element.width, 6 # TODO: Get size from mat, then from track
                    )

                    Sectorizer.auto_put(trajectory)
                    scn.trajectory_tools.profile.set_instance(trajectory, profile)

                    trajectory_tools.set_material(trajectory, HelperMATImporter.import_material_from_relpath(element.map1), 0)
                    trajectory_tools.set_material(trajectory, HelperMATImporter.import_material_from_relpath(element.map2), 1)

                    obj = trajectory

                elif element.subtype in "switch":
                    trajectory_straight = self._trajectory_builder.build_trajectory(element)
                    self._trajectory_builder.create_spline(trajectory_straight, element.p1, element.cv1, element.p2, element.cv2, element.p1_roll, element.p2_roll)
                    trajectory_side = self._trajectory_builder.build_trajectory(element)
                    self._trajectory_builder.create_spline(trajectory_side, element.p3, element.cv3, element.p4, element.cv4, element.p1_roll, element.p2_roll)

                    Sectorizer.auto_put(trajectory_straight)
                    Sectorizer.auto_put(trajectory_side)

                    trajectory_side.parent = trajectory_straight
                    trajectory_side.location = (0, 0, 0)

                    obj = trajectory_straight

                obj.eu07_include_identifier = self._include_identifier

        self.init_switches()
        obj = self._terrain_builder.finish()
        obj.eu07_include_identifier = self._include_identifier

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
                            trajectory_tools.profile.copy_instance_between(neighbour, trajectory_straight)
                            trajectory_tools.profile.copy_instance_between(neighbour, trajectory_side)

                            trajectory_tools.set_material(trajectory_straight, ballast_mat, 1)
                            trajectory_tools.set_material(trajectory_side, ballast_mat, 1)
                            break