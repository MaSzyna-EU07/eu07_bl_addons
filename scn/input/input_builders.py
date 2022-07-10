import math
import pathlib

import bpy
import eu07_tools
import scn.trajectory_tools.profile

from scn.decorations import DecorationsBuilder
from scn.trajectory_tools.trajectory_builder import TrajectoryBuilder
from scn.terrain import TerrainBuilder
from scn import trajectory_tools
from scn.core import factory
from scn.sectorizer import Sectorizer
from material_tools.input import MaterialImporter
from common import includes
import scn


class SceneryImporter:
    def __init__(self):
        pass

    def import_from_filepath(self, filepath):
        pass

    def import_from_file(self, file):
        pass

#TODO: Material lookup
#TODO: Prevent mesh_data from regeneration after each property update
    def _import_track(self, track_element):
        track_entity = factory.create_entity(track_element.type, track_element.name)
        track_entity.width = track_element.width
        track_entity.friction = track_element.friction
        track_entity.sound_distance = track_element.sound_distance
        track_entity.quality_flag = track_element.quality_flag
        track_entity.damage_flag = track_element.damage_flag
        track_entity.environment = track_element.environment
        track_entity.visibility = "vis" if track_element.is_visible else "unvis"
        track_entity.map1 = None
        track_entity.map1_length = track_element.mapping_length
        track_entity.map2 = None
        track_entity.geometry_params = track_element.geometry_params

        track_entity.p1 = track_element.p1
        track_entity.p1_roll = track_element.p1_roll

        track_entity.cv1 = track_element.cv1
        track_entity.cv2 = track_element.cv2

        track_entity.p2 = track_element.p2
        track_entity.p2_roll = track_element.p2_roll

        if track_element.is_junction:
            track_entity.p3 = track_element.p3
            track_entity.p3_roll = track_element.p3_roll

            track_entity.cv3 = track_element.cv3
            track_entity.cv4 = track_element.cv4

            track_entity.p4 = track_element.p4
            track_entity.p4_roll = track_element.p4_roll

        track_entity.radius1 = track_element.radius1
        track_entity.radius2 = track_element.radius2

        track_entity.velocity = track_element.velocity

        track_entity.event0_name = track_element.event0
        track_entity.event1_name = track_element.event1
        track_entity.event2_name = track_element.event2

        track_entity.eventall0_name = track_element.eventall0
        track_entity.eventall1_name = track_element.eventall1
        track_entity.eventall2_name = track_element.eventall2

        track_entity.isolated_name = track_element.isolated
        track_entity.overhead = track_element.overhead

        track_entity.angle1 = track_element.angle1
        track_entity.angle2 = track_element.angle2

        track_entity.fouling1 = track_element.fouling1
        track_entity.fouling2 = track_element.fouling2

        track_entity.railprofile = track_element.railprofile

        track_entity.friction_memcell = track_element.friction_memcell_name

class SceneryBuilder:
    def __init__(self, config, include_identifier=-1):
        self._config = config
        self._trajectory_builder = TrajectoryBuilder()
        self._terrain_builder = TerrainBuilder(config)
        self._decoration_builder = DecorationsBuilder(config)
        self._include_identifier = include_identifier

    def run(self, data):
        assearch = self._config["asset_searcher"]

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

                        material = MaterialImporter(assearch).import_from_relpath(element.parameters[0])
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

                    trajectory_tools.set_material(trajectory, MaterialImporter(assearch).import_from_relpath(element.map1), 0)
                    trajectory_tools.set_material(trajectory, MaterialImporter(assearch).import_from_relpath(element.map2), 1)

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
                    for i in range(4):
                        part_trajectory = trajectory_straight if i < 1 else trajectory_side

                        point_index = i - 1 if i > 1 else i + 1

                        neighbour = trajectory_tools.get_neighbour(part_trajectory, point_index)
                        if neighbour is not None:
                            ballast_mat = trajectory_tools.get_material(neighbour, 1)
                            trajectory_tools.profile.copy_instance_between(neighbour, trajectory_straight)
                            trajectory_tools.profile.copy_instance_between(trajectory_straight, trajectory_side)

                            trajectory_tools.set_material(trajectory_straight, ballast_mat, 1)
                            trajectory_tools.set_material(trajectory_side, ballast_mat, 1)
                            break