import math
import bpy
from bpy_extras import view3d_utils

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
    def iter_visible_sectors():
        for collection in bpy.context.scene.collection.children:
            if collection.name.startswith("sector"):
                yield collection

    @staticmethod
    def iter_all_sectors():
        for collection in bpy.data.collections:
            if collection.name.endswith("sector"):
                yield collection

    @staticmethod
    def get_sector_by_location(location):
        if Sectorizer.sector_size == 0:
            return bpy.context.scene.collection

        return Sectorizer.get_sector_by_id(Sectorizer.specify_id(location))

    @staticmethod
    def insert_into_sector(obj, sector):
        sector.objects.link(obj)

    @staticmethod
    def link_sectors(sectors):
        for sector in sectors:
            bpy.context.scene.collection.children.link(sector)

    @staticmethod
    def unlink_sectors(sectors):
        for sector in sectors:
            bpy.context.scene.collection.children.unlink(sector)

    @staticmethod
    def _format_id(x, y):
        return f"sector x{x} y{y}"


class SCN_OT_LoadSectors(bpy.types.Operator):
    bl_idname = "scn.load_sectors"
    bl_label = "Load sectors around camera"

    def execute(self, context):
        # BUG: Rail profiles don't want to link :/
        camera_location = view3d_utils.region_2d_to_origin_3d(context.region, context.space_data.region_3d, (0.5, 0.5))
        Sectorizer.unlink_sectors(Sectorizer.iter_visible_sectors())
        Sectorizer.link_sectors([Sectorizer.get_sector_by_location(camera_location)])

        return {'FINISHED'}
