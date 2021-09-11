from pathlib import Path
import os

import bpy
from bpy.props import IntProperty, EnumProperty, BoolProperty

from common import get_root


class BasemapProperties(bpy.types.PropertyGroup):
    basemap_puwg_x: IntProperty(
        name="PUWG1992 X Coordinate"
    )

    basemap_puwg_y: IntProperty(
        name="PUWG1992 Y Coordinate"
    )

    basemap_type: EnumProperty(
        name="Basemap Type",
        items=(
            ("pl1topo", "Topo", ""),
            ("pl4000px", "Ortho Basic", ""),
            ("pl4k'03", "Ortho 2003", ""),
            ("pl4k'09", "Ortho 2009", ""),
            ("pl4k'13", "Ortho 2013", ""),
            ("pl4k'15", "Ortho 2015", ""),
            ("pl4k'18", "Ortho 2018", ""),
        )
    )

    basemap_use_cursor: BoolProperty(
        name="Use 3D Cursor",
        default=False
    )

    basemap_limit: IntProperty(
        name="Area limit",
        default=2000,
        min=100
    )


class BasemapPanel(bpy.types.Panel):
    bl_idname = "SCENE_PT_basemap"
    bl_label = "Aerial Photos Basemap"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "[EU07] SCN Editor"

    def draw(self, context):
        scene = context.scene

        box = self.layout.box()
        box.label(text="PUWG1992 coordinates")
        row = box.row()
        row.prop(scene.eu07_properties, "basemap_puwg_x", text="X")
        row.prop(scene.eu07_properties, "basemap_puwg_y", text="Y")

        # self.layout.prop(scene.eu07_properties, "basemap_use_cursor", text="Load in 3D cursor area")
        self.layout.prop(scene.eu07_properties, "basemap_limit", text="Loading radius limit")

        self.layout.prop(scene.eu07_properties, "basemap_type", text="Map type")
        self.layout.operator("scene.eu07_load_basemaps")


class LoadBasemapOperator(bpy.types.Operator):
    bl_idname = "scene.eu07_load_basemaps"
    bl_label = "Load basemaps from EU07 gisdata"

    def invoke(self, context, event):
        collection = bpy.data.collections.get("Basemaps")
        if (collection is None):
            collection = bpy.data.collections.new("Basemaps")
            context.scene.collection.children.link(collection)

        for o in collection.objects:
            bpy.data.objects.remove(o)

        for img in bpy.data.images:
            if img.users == 0:
                bpy.data.images.remove(img)

        return self.execute(context)

    def execute(self, context):
        collection = bpy.data.collections.get("Basemaps")

        puwg_center_x = bpy.context.scene.eu07_properties.basemap_puwg_x
        puwg_center_y = bpy.context.scene.eu07_properties.basemap_puwg_y
        limit = bpy.context.scene.eu07_properties.basemap_limit
        cursor_loc = bpy.context.scene.cursor.location

        root = get_root()
        dirpath = Path(root, "gisdata", context.scene.eu07_properties.basemap_type)

        for filename in os.listdir(dirpath):

            image_loc = mathutils.Vector((
                (int(filename[:4]) - puwg_center_x) * 100 + 50,
                (int(filename[4:8]) - puwg_center_y) * 100 + 50,
                0
            ))

            should_be_loaded = ((image_loc - cursor_loc).length < limit)

            if should_be_loaded:
                basemap_name = f"BASEMAP_{filename[:-4]}"

                if basemap_name in bpy.data.objects:
                    continue

                quad = bpy.data.objects.new(basemap_name, None)
                quad.empty_display_type = 'IMAGE'
                quad.show_empty_image_orthographic = True
                quad.empty_display_size = 100

                image = bpy.data.images.load(str(dirpath / filename), check_existing=True)
                image.name = basemap_name
                quad.data = image

                quad.location.x = image_loc.x
                quad.location.y = image_loc.y

                quad.hide_select = True

                collection.objects.link(quad)

        return {'FINISHED'}