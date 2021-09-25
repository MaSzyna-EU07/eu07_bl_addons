from typing import Sequence

import bpy
from bpy_extras import view3d_utils


def ray_cast_to_terrain(mouse_pos: Sequence[float]) -> float:
    region = bpy.context.region
    region_data = bpy.context.space_data.region_3d

    location = view3d_utils.region_2d_to_origin_3d(region, region_data, mouse_pos)
    direction = view3d_utils.region_2d_to_vector_3d(region, region_data, mouse_pos)

    hit_point = (0, 0, 0)

    depsgraph = bpy.context.evaluated_depsgraph_get()
    while True:
        hit, location, normal, index, obj, matrix = \
            bpy.context.scene.ray_cast(depsgraph, location + direction * 0.0001, direction)

        if obj.scn_properties.type_ == "node:triangles":
            return location
