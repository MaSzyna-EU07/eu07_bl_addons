import math
import bpy
from bpy_extras import view3d_utils


# TODO: Shouldn't it be in module instead making static methods?
class Sectorizer:
    sector_size = 2000

    @staticmethod
    def auto_put(obj):
        try:
            sector = Sectorizer.get_sector_by_location(obj.location)
            Sectorizer.insert_into_sector(obj, sector)
            for child in obj.children:
                Sectorizer.insert_into_sector(child, sector)
        except RuntimeError: # when obj is in collection already
            pass



    @staticmethod
    def auto_put_iterable(objects):
        for obj in objects:
            Sectorizer.auto_put(obj)

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
    def show_sectors(sectors):
        # BUG: Rail profiles don't want to link :/
        for sector in sectors:
            sector.hide_viewport = False

    @staticmethod
    def hide_sectors(sectors):
        for sector in sectors:
            sector.hide_viewport = True

    @staticmethod
    def _format_id(x, y):
        return f"sector x{x} y{y}"


class SCN_OT_LoadSectors(bpy.types.Operator):
    bl_idname = "scn.load_sectors"
    bl_label = "Load sectors around camera"

    def execute(self, context):
        camera_location = view3d_utils.region_2d_to_origin_3d(context.region, context.space_data.region_3d, (0.5, 0.5))
        Sectorizer.hide_sectors(Sectorizer.iter_visible_sectors())
        Sectorizer.show_sectors([Sectorizer.get_sector_by_location(camera_location)])

        return {'FINISHED'}


class SCN_OT_PutSelectedIntoSectors(bpy.types.Operator):
    bl_idname = "scn.put_selected_into_sectors"
    bl_label = "Put selection into sectors"

    def execute(self, context):
        Sectorizer.auto_put_iterable(context.selected_objects)

        return {'FINISHED'}


class SCN_PT_Sectorizer(bpy.types.Panel):
    bl_idname = "SCN_PT_Sectorizer"
    bl_label = "Sectorizer"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "[EU07] SCN Editor"

    def draw(self, context):
        load_sectors_row = self.layout.row()
        load_sectors_row.operator('scn.load_sectors')


classes = (
    SCN_OT_LoadSectors,
    SCN_PT_Sectorizer,
    SCN_OT_PutSelectedIntoSectors
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # bpy.types.Scene.scn_sectorizer = bpy.props.IntProperty(min=0, max=3000, default=2000)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
