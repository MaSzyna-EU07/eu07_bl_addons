import bpy

from .trajectory_builder import TrajectoryBuilder

from . import sector


class SceneryBuilder:
    def __init__(self, config):
        self._tracks_builder = TrajectoryBuilder(config)

    def run(self, data):
        for element in data:
            if element.type == "node:track":
                o = bpy.data.objects.new(element.name, None)
                sector.put(o, element.p1.swizzled())
