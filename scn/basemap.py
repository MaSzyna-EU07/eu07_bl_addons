from pathlib import Path
import os
import mathutils

import bpy
from ..common import get_root

class LoadBasemapPanel(bpy.types.Panel):
    bl_idname = "SCENE_PT_eu07_load_basemaps"
    bl_label = "[EU07] Load Basemaps"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        scene = context.scene

        box = self.layout.box()
        box.label(text="PUWG1992 coordinates")
        row = box.row()
        row.prop(scene.eu07_properties, "basemap_puwg_x", text="X")
        row.prop(scene.eu07_properties, "basemap_puwg_y", text="Y")

        #self.layout.prop(scene.eu07_properties, "basemap_use_cursor", text="Load in 3D cursor area")
        self.layout.prop(scene.eu07_properties, "basemap_limit", text="Loading radius limit")

        self.layout.prop(scene.eu07_properties, "basemap_type", text="Map type")
        self.layout.operator("scene.eu07_load_basemaps")

class LoadBasemapOperator(bpy.types.Operator):
    bl_idname = "scene.eu07_load_basemaps"
    bl_label = "Load basemaps from EU07 gisdata"

    def execute(self, context):
        type_ = bpy.context.scene.eu07_properties.basemap_type
        if type_ not in bpy.data.collections:
            collection = bpy.data.collections.new(type_)
            bpy.context.scene.collection.children.link(collection)
        else:
            collection = bpy.data.collections[type_]

        puwg_center_x = bpy.context.scene.eu07_properties.basemap_puwg_x
        puwg_center_y = bpy.context.scene.eu07_properties.basemap_puwg_y
        limit = bpy.context.scene.eu07_properties.basemap_limit
        cursor_loc = bpy.context.scene.cursor.location

        root = get_root()
        dirpath = Path(root, "gisdata", type_)

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

                collection.objects.link(quad)
        
        return {'FINISHED'}



    