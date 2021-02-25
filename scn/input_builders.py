import bpy

from .trajectory_builder import TrajectoryBuilder
from . import trajectory_utils
from common import create_material_from_relpath
from . import sector_utils
import eu07_tools


class SceneryBuilder:
    def __init__(self):
        self._trajectory_builder = TrajectoryBuilder()

    def run(self, data):
        for element in data:
            if element.type == "node:track":
                if element.subtype in "normal road river":
                    trajectory = self._trajectory_builder.build_trajectory(element)
                    self._trajectory_builder.create_spline(trajectory, element.p1, element.cv1, element.p2, element.cv2)
                    profile = trajectory_utils.create_profile_instance(
                        element.subtype, element.geometry_params, element.width, 6 # TODO: Get size from mat, then from track
                    )

                    sector = sector_utils.get_sector_by_location(trajectory.location)

                    sector_utils.insert_into_sector(trajectory, sector)
                    trajectory_utils.set_profile_instance(trajectory, profile)

                    trajectory_utils.set_material(trajectory, create_material_from_relpath(element.map1), 0)
                    trajectory_utils.set_material(trajectory, create_material_from_relpath(element.map2), 1)

                elif element.subtype in "switch":
                    trajectory_straight = self._trajectory_builder.build_trajectory(element)
                    self._trajectory_builder.create_spline(trajectory_straight, element.p1, element.cv1, element.p2, element.cv2)
                    trajectory_side = self._trajectory_builder.build_trajectory(element)
                    self._trajectory_builder.create_spline(trajectory_side, element.p3, element.cv3, element.p4, element.cv4)

                    sector = sector_utils.get_sector_by_location(trajectory_straight.location)

                    sector_utils.insert_into_sector(trajectory_straight, sector)
                    sector_utils.insert_into_sector(trajectory_side, sector)

                    trajectory_side.parent = trajectory_straight
                    trajectory_side.location = (0, 0, 0)

        self.init_switches()



            # elif element.type == "include" and element.path.endswith(".inc"):
            #     inc = bpy.data.objects.new("include", None)
            #     inc.location = eu07_tools.utils.switch_coordinate_system([float(p) for p in element.parameters[1:4]])
            #     sector = sector_utils.get_sector_by_location(inc.location)
            #
            #     sector_utils.insert_into_sector(inc, sector)


    def init_switches(self):
        for o in bpy.data.objects:
            if o.type == 'CURVE':
                trajectory = o
                if trajectory.scn_properties.type_ == "node:track:switch" and trajectory.parent is None:
                    for i in range(4):
                        trajectory_straight = trajectory
                        trajectory_side = trajectory_utils.get_switch_side(trajectory_straight)

                        part_trajectory = trajectory_straight if i > 1 else trajectory_side

                        point_index = i - 1 if i > 1 else i + 1

                        neighbour = trajectory_utils.get_neighbour(part_trajectory, point_index)
                        if neighbour is not None:
                            ballast_mat = trajectory_utils.get_material(neighbour, 1)
                            trajectory_utils.copy_profile_instance(neighbour, trajectory_straight)
                            trajectory_utils.copy_profile_instance(neighbour, trajectory_side)

                            trajectory_utils.set_material(trajectory_straight, ballast_mat, 1)
                            trajectory_utils.set_material(trajectory_side, ballast_mat, 1)