import math
import bpy


class Sectorizer:
    sector_size = 2000

    @staticmethod
    def auto_put(obj):
        Sectorizer.insert_into_sector(obj, Sectorizer.get_sector_by_location(obj.location))

    @staticmethod
    def specify_id(location):
        ids = [0, 0]
        for i in range(2):
            coord = abs(location[i])
            if coord != 0:
                coord_sign = coord / location[i]
            else:
                coord_sign = 1

            if coord >= Sectorizer.sector_size:
                ids[i] = int(coord // Sectorizer.sector_size * coord_sign)
            else:
                ids[i] = int(round(coord / Sectorizer.sector_size) * coord_sign)

        return f"x{ids[0]} y{ids[1]}"

    @staticmethod
    def get_sector_by_id(sector_id):
        if Sectorizer.sector_size == 0:
            return bpy.context.scene.collection

        sector = bpy.data.collections.get(sector_id)
        if sector is None:
            sector = bpy.data.collections.new(sector_id)
            bpy.context.scene.collection.children.link(sector)

        return sector

    @staticmethod
    def get_sector_by_location(location):
        if Sectorizer.sector_size == 0:
            return bpy.context.scene.collection

        return Sectorizer.get_sector_by_id(Sectorizer.specify_id(location))

    @staticmethod
    def insert_into_sector(obj, sector):
        sector.objects.link(obj)
