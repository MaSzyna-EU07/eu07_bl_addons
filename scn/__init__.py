from pathlib import Path
import os
import sys

import bpy
from bpy.props import StringProperty, IntProperty, EnumProperty, BoolProperty, FloatProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper
import eu07_tools

from ..common import get_root
from .input_builders import SceneryBuilder
from .output_builders import create_node_triangles_from_mesh, create_node_track
from .basemap import LoadBasemapOperator, LoadBasemapPanel

class SCNImport(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.scn"
    bl_label = "Import SCN"

    filter_glob: StringProperty(
        default="*.scn;*.scm;*.inc",
        options={'HIDDEN'}
    )

    import_terrain: BoolProperty(
        name="Import Terrain",
        default=True
    )

    import_tracks: BoolProperty(
        name="Import Tracks",
        default=True
    )

    import_roads: BoolProperty(
        name="Import Roads",
        default=True
    )

    import_rivers: BoolProperty(
        name="Import Rivers",
        default=True
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
            
            tracks = []
            for o in objects:
                if 'node:triangles' in o.scn_properties.type_:
                    eu07_tools.scn.dump(create_node_triangles_from_mesh(o.data.copy()), outfile)
                if 'node:track' in o.scn_properties.type_:
                    tracks.append(create_node_track(o))

            eu07_tools.scn.dump(tracks, outfile)

        return {'FINISHED'}

def update_material_list(self, context):
    items = []
    for mat in bpy.data.materials:
        items.append((mat.name, mat.name, ""))

    return items

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

class SCNObjectProperties(bpy.types.PropertyGroup):
    type_: EnumProperty(
        name="Type",
        default="other",
        items=[
            ("other", "Other", ""),
            ("node:track:normal", "Railroad Track", ""),
            ("node:track:switch", "Railroad Switch", ""),
            ("node:track:turn", "Railroad Turn", ""),
            ("node:track:table", "Railroad Table", ""),
            ("node:track:road", "Road", ""),
            ("node:track:cross", "Road Cross", ""),
            ("node:track:river", "River", ""),
            ("node:track:tributary", "River Tributary", ""),
            ("node:sound", "Sound Source", ""),
            ("node:triangles", "Terrain", ""),
            ("node:lines", "Lines", ""),
            ("origin", "Origin", ""),
            ("camera", "Camera", ""),
            ("include", "Include", ""),
        ]
    )

    node_max_distance: FloatProperty(
        name='Max Distance',
        min=-1,
        default=-1,
        step=0.1,
        unit='LENGTH'
    )

    node_min_distance: FloatProperty(
        name='Min Distance',
        min=0,
        step=0.1,
        unit='LENGTH'
    )

    trajectory_width: FloatProperty(
        name='Width',
        default=1.435,
        min=0,
        step=0.001,
        unit='LENGTH'
    )

    trajectory_friction: FloatProperty(
        name='Friction',
        default=0.15,
        min=0,
        step=0.01,
    )

    trajectory_sound_distance: FloatProperty(
        name='Sound distance',
        default=20,
        min=0,
        step=0.01,
        unit='LENGTH'
    )

    trajectory_quality: IntProperty(
        name='Quality',
        default=0,
        min=0,
        max=255,
        step=1,
    )

    trajectory_damage: IntProperty(
        name='Damage',
        default=0,
        min=0,
        max=255,
        step=1,
    )

    trajectory_environment: EnumProperty(
        name="Environment",
        default="flat",
        items=[
            ("flat", "Flat", ""),
            ("mountains", "Mountains", ""),
            ("canyon", "Canyon", ""),
            ("tunnel", "Tunnel", ""),
            ("bridge", "Bridge", ""),
            ("bank", "Bank", ""),
        ]
    )

    trajectory_visible: BoolProperty(
        name="Is Visible",
        default=True
    )

    trajectory_p1_roll: FloatProperty(
        name='P1 roll',
        default=0,
        min=0,
        step=0.001,
        unit='ROTATION'
    )

    trajectory_p2_roll: FloatProperty(
        name='P2 roll',
        default=0,
        min=0,
        step=0.001,
        unit='ROTATION'
    )

    trajectory_map1: EnumProperty(
        name="Materials",
        items=update_material_list 
    )

    trajectory_map2: EnumProperty(
        name="Materials",
        items=update_material_list 
    )

    trajectory_mapping_length: FloatProperty(
        name='Mapping length',
        default=0,
        min=0,
        step=0.001,
        unit='LENGTH'
    )
    

class SCNObjectPropertiesPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_scn"
    bl_label = "[EU07] SCN Object Properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    def draw(self, context):
        self.obj = context.object

        type_r = self.layout.row()
        type_r.prop(self.obj.scn_properties, "type_")

        if ("node:" in self.obj.scn_properties.type_):
            name_r = self.layout.row()
            name_r.prop(self.obj, "name")

            maxdistance_r = self.layout.row()
            maxdistance_r.prop(self.obj.scn_properties, "node_max_distance")

            mindistance_r = self.layout.row()
            mindistance_r.prop(self.obj.scn_properties, "node_min_distance")

        if ("node:track" in self.obj.scn_properties.type_):
            if (self.obj.type != 'CURVE'):
                self.layout.label(text="Trajectory must be a Curve!")
            else:
                width_r = self.layout.row()
                width_r.prop(self.obj.scn_properties, "trajectory_width")

                friction_r = self.layout.row()
                friction_r.prop(self.obj.scn_properties, "trajectory_friction")

                sound_distance_r = self.layout.row()
                sound_distance_r.prop(self.obj.scn_properties, "trajectory_sound_distance")

                quality_r = self.layout.row()
                quality_r.prop(self.obj.scn_properties, "trajectory_quality")

                damage_r = self.layout.row()
                damage_r.prop(self.obj.scn_properties, "trajectory_damage")

                environment_r = self.layout.row()
                environment_r.prop(self.obj.scn_properties, "trajectory_environment")

                visible_r = self.layout.row()
                visible_r.prop(self.obj.scn_properties, "trajectory_visible")

                p1_roll_r = self.layout.row()
                p1_roll_r.prop(self.obj.scn_properties, "trajectory_p1_roll")

                p2_roll_r = self.layout.row()
                p2_roll_r.prop(self.obj.scn_properties, "trajectory_p2_roll")

                track_subtype = self.obj.scn_properties.type_.split(":")[-1]

                if (track_subtype in "normal turn table"):
                    map1_label = "Rails Material"
                    map2_label = "Ballast Material"
                elif (track_subtype in "road cross"):
                    map1_label = "Road Material"
                    map2_label = "Side Material"
                elif (track_subtype in "river tributary"):
                    map1_label = "Water Material"
                    map2_label = "Bank Material"
                elif (track_subtype in "switch"):
                    map1_label = "Rails Material Straight"
                    map2_label = "Rails Material Sideway"










