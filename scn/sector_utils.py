import math
import bpy

SIZE = 2000


def specify_id(location):
    ids = [0, 0]
    for i in range(2):
        coord = abs(location[i])
        if coord != 0:
            coord_sign = coord / location[i]

        if coord >= SIZE:
            ids[i] = int(coord // SIZE * coord_sign)
        else:
            ids[i] = int(round(coord / SIZE) * coord_sign)

    return f"x{ids[0]} y{ids[1]}"


def get_sector_by_id(sector_id):
    sector = bpy.data.collections.get(sector_id)
    if sector is None:
        sector = bpy.data.collections.new(sector_id)
        bpy.context.scene.collection.children.link(sector)

    return sector


def get_sector_by_location(location):
    return get_sector_by_id(specify_id(location))


def insert_into_sector(obj, sector):
    sector.objects.link(obj)
