import bpy

from .trajectory_builder import TrajectoryBuilder, instantiate_trajectory_profile

from . import sector_utils
from .utils import  set_trajectory_profile, set_trajectory_material, load_trajectory_materials
import eu07_tools


class SceneryBuilder:
    def __init__(self, config):
        self._config = config
        self._trajectory_builder = TrajectoryBuilder(config)

    def run(self, data):
        for element in data:
            if element.type == "node:track":
                if element.subtype in "normal road river":
                    trajectory = self._trajectory_builder.build_trajectory(element)
                    profile = instantiate_trajectory_profile(
                        element.subtype, element.geometry_params, element.width, element.mapping_length
                    )

                    sector = sector_utils.get_sector_by_location(trajectory.location)

                    sector_utils.insert_into_sector(trajectory, sector)
                    sector_utils.insert_into_sector(profile, sector)

                    set_trajectory_profile(trajectory, profile)

                    mats = load_trajectory_materials([element.map1, element.map2], self._config["asset_searcher"])

                    set_trajectory_material(trajectory, mats[0], 0)
                    set_trajectory_material(trajectory, mats[1], 1)

            elif element.type == "include" and element.path.endswith(".inc"):
                inc = bpy.data.objects.new("include", None)
                inc.location = eu07_tools.utils.switch_coordinate_system([float(p) for p in element.parameters[1:4]])
                sector = sector_utils.get_sector_by_location(inc.location)

                sector_utils.insert_into_sector(inc, sector)




