from pathlib import Path
import os

import bpy
from bpy.props import StringProperty, IntProperty, EnumProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
import eu07_tools.scn
from eu07_tools.utils import AssetSearcher, find_root

from .input_builders import SceneryBuilder

class SCNImport(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.scn"
    bl_label = "Import SCN"

    filter_glob: StringProperty(
        default="*.scn;*.scm;*.inc",
        options={'HIDDEN'}
    )

    def execute(self, context):
        root = find_root(self.filepath)

        asset_searcher = AssetSearcher(root, Path(self.filepath).parent)
        asset_searcher.textures_finder.remove_extension(".mat")

        config = {
            "asset_searcher": asset_searcher
        }

        scn_input = eu07_tools.scn.load(open(self.filepath, encoding='latin-1'))

        builder = SceneryBuilder(config)
        builder.run(scn_input)

        del builder
        
        return {'FINISHED'}


class EU07SceneryProperties(bpy.types.PropertyGroup):
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
        default=20,
        min=1
    )


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

        self.layout.prop(scene.eu07_properties, "basemap_use_cursor", text="Load in 3D cursor area")
        self.layout.prop(scene.eu07_properties, "basemap_limit", text="Loading radius limit")

        self.layout.prop(scene.eu07_properties, "basemap_type", text="Map type")
        self.layout.operator("scene.eu07_load_basemaps")

class LoadBasemapOperator(bpy.types.Operator):
    bl_idname = "scene.eu07_load_basemaps"
    bl_label = "Load basemaps from EU07 gisdata"

    def execute(self, context):
        puwg_center_x = context.scene.eu07_properties.basemap_puwg_x
        puwg_center_y = context.scene.eu07_properties.basemap_puwg_x
        basemap_type = context.scene.eu07_properties.basemap_type

        # TODO: Get from userprefs
        root = "/run/media/krzysiu/246692DC6692ADD4/MaSzyna 17.07"

        basemaps_collection = bpy.data.collections.get("basemaps")
        if not basemaps_collection:
            basemaps_collection = bpy.data.collections.new("basemaps")

        basemap_specific_collection = bpy.data.collections.new(basemap_type)
        
        basemaps_collection.children.link(basemap_specific_collection)

        basemap_dir = Path(root, "gisdata", basemap_type)


        for image_name in os.listdir(basemap_dir):

            basemap_name = f"BASEMAP_{basemap_type}_{image_name[:-3]}"
            quad = bpy.data.objects.new(basemap_name, None)
            quad.empty_display_type = 'IMAGE'
            quad.show_empty_image_orthographic = True
            quad.empty_display_size = 100
            quad.use_empty_image_alpha = True
            quad.color[3] = 0.5 # Transparency level

            image = bpy.data.images.load(str(basemap_dir / image_name), check_existing=True)
            image.name = basemap_name
            quad.data = image

            image_x, image_y = int(image_name[:4]), int(image_name[4:8])

            quad.location[0] = (image_x - puwg_center_x) * 100
            quad.location[1] = (image_y - puwg_center_y) * 100

            print(image_name, quad.location[0], quad.location[1])

            bpy.context.scene.collection.objects.link(quad)
            basemap_specific_collection.objects.link(quad)

        return {'FINISHED'}



