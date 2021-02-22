import bpy

from .trajectory_builder import TrajectoryBuilder

from . import sector


class SceneryBuilder:
    def __init__(self, config):
        self._trajectory_builder = TrajectoryBuilder(config)

    def run(self, data):
        for element in data:
            if element.type == "node:track":
                o = self._trajectory_builder.build_trajectory(element)
                sector.put(o, element.p1.swizzled())
