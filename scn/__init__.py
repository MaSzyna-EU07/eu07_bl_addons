from pathlib import Path
import os
import sys

import bpy
from bpy.props import StringProperty, IntProperty, EnumProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper
import eu07_tools

from eu07_bl_addons.common import get_root
from .input_builders import SceneryBuilder
from .output_builders import create_node_triangles_from_mesh
from .basemap import LoadBasemapOperator, LoadBasemapPanel

class SCNImport(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.scn"
    bl_label = "Import SCN"

    filter_glob: StringProperty(
        default="*.scn;*.scm;*.inc",
        options={'HIDDEN'}
    )

    def execute(self, context):
        root = get_root(self.filepath)

        asset_searcher = eu07_tools.utils.AssetSearcher(
            root, Path(self.filepath).parent
        )
        asset_searcher.textures.remove_extension(".mat")

        config = {
            "asset_searcher": asset_searcher
        }

        with open(self.filepath, encoding='latin-1') as infile:
            scn_input = eu07_tools.scn.load(infile)

            builder = SceneryBuilder(config)
            builder.run(scn_input)

        del builder
        
        return {'FINISHED'}


class SCNExport(bpy.types.Operator, ExportHelper):
    bl_idname = "export_scene.scn"
    bl_label = "Export SCN"
    filename_ext = ".scm"

    filter_glob: StringProperty(
        default="*.scn;*.scm;*.inc",
        options={'HIDDEN'}
    )
    use_selection: BoolProperty(
        name="Use selection",
        default=False
    )

    def execute(self, context):
        with open(self.filepath, mode="w", encoding="windows-1250", newline="\r\n") as outfile:
            if self.use_selection:
                objects = [o for o in bpy.data.objects if o.select_get()]
            else:
                objects = bpy.data.objects
                
            for o in objects:
                if o.type == "MESH":
                    eu07_tools.scn.dump(create_node_triangles_from_mesh(o.data.copy()), outfile)

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
        default=2000,
        min=100
    )






