import math
import bpy

SIZE = 2000


def specify_id(location):
    ids = [0, 0]
    for i in range(2):
        coord = abs(location[i])
        coord_sign = coord / location[i]

        if coord >= SIZE:
            ids[i] = int(coord // SIZE * coord_sign)
        else:
            ids[i] = int(round(coord / SIZE) * coord_sign)

    return f"x{ids[0]} y{ids[1]}"


def put(obj, location):
    obj.location = location
    sector_id = specify_id(obj.location)
    sector_collection = bpy.data.collections.get(sector_id)
    if sector_collection is None:
        sector_collection = bpy.data.collections.new(sector_id)
        bpy.context.scene.collection.children.link(sector_collection)

    for c in obj.children:
        sector_collection.objects.link(c)

    sector_collection.objects.link(obj)
