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

        return Sectorizer._format_id(ids[0], ids[1])

    # TODO: Remove side effect - add 'default': Collection paramater
    @staticmethod
    def get_sector_by_id(sector_id, create=True):
        if Sectorizer.sector_size == 0:
            return bpy.context.scene.collection

        sector = bpy.data.collections.get(sector_id)
        if sector is None and create:
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

    def show_sectors_around(self, center, radius=2000):
        center_sector = self.specify_id(center)

        # hardcoded at the moment
        offsets = [
            [0, 1],
            [1, 1],
            [1, 0],
            [1, -1],
            [0, -1],
            [-1, -1],
            [-1, 0],
            [-1, 1]
        ]

        sectors_to_show = []

        for offset in offsets:
            sector_id = Sectorizer._format_id(offset[0], offset[1])
            sector = Sectorizer.get_sector_by_id(sector_id)
            if sector:
                sectors_to_show.append(sector)

        Sectorizer.link_sectors(sectors_to_show)

    @staticmethod
    def link_sectors(self, sectors):
        for sector in sectors:
            bpy.context.scene.collection.children.link(sector)

    @staticmethod
    def _format_id(self, x, y):
        return f"sector x{x} y{y}"