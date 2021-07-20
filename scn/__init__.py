from pathlib import Path
import os
import sys

import bpy
from bpy.props import StringProperty, IntProperty, EnumProperty, BoolProperty, FloatProperty, FloatVectorProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper
import eu07_tools

from ..common import get_root
from .input_builders import SceneryBuilder
from .output_builders import create_node_triangles_from_mesh, create_node_track

from . import trajectory_utils
from .sectorizer import Sectorizer

import mathutils


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

    inc_recursion_depth: IntProperty(
        name="Include recursion depth",
        default=1
    )

    weld_terrain: BoolProperty(
        name="Weld Terrain Triangles",
        default=True
    )

    cache_tracks_neighbours: BoolProperty(
        name="Cache Tracks Neibourghs"
    )

    sector_size: IntProperty(
        name="Sector Size",
        default=0,
        min=0
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

        Sectorizer.sector_size = self.sector_size

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
                    is_junction_track = (o.parent is not None)
                    if not is_junction_track:
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


class LoadBasemapPanel(bpy.types.Panel):
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


def update_visibility(self, context):
    obj = context.active_object

    if obj is None: return

    if obj.scn_properties.type_.startswith("node:track"):
        profile_instance = trajectory_utils.get_profile_instance(obj)
        profile_instance.hide_set(not context.active_object.scn_properties.trajectory_visible)


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

    trajectory_profile_param1: FloatProperty(
        name="Param 1",
        default=0.2,
        update=trajectory_utils.update_profile_instance
    )

    trajectory_profile_param2: FloatProperty(
        name="Param 2",
        default=0.5,
        update=trajectory_utils.update_profile_instance
    )

    trajectory_profile_param3: FloatProperty(
        name="Param 3",
        default=1.3,
        update=trajectory_utils.update_profile_instance
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
        default=True,
        update=update_visibility
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

    trajectory_mapping_length: FloatProperty(
        name='Mapping length',
        default=0,
        min=0,
        step=0.001,
        unit='LENGTH'
    )

    trajectory_velocity: FloatProperty(
        name='Velocity',
        default=0,
        min=0,
        step=1,
        unit='VELOCITY'
    )

    trajectory_event0: StringProperty(
        name='Event 0',
        default=""
    )

    trajectory_event1: StringProperty(
        name='Event 1',
        default=""
    )

    trajectory_event2: StringProperty(
        name='Event 2',
        default=""
    )

    trajectory_eventall0: StringProperty(
        name='EventAll 0',
        default=""
    )

    trajectory_eventall1: StringProperty(
        name='EventAll 1',
        default=""
    )

    trajectory_eventall2: StringProperty(
        name='EventAll 2',
        default=""
    )

    trajectory_isolated: StringProperty(
        name='Isolated',
        default=""
    )

    trajectory_overhead: IntProperty(
        name='Overhead',
        default=0
    )

    trajectory_angle1: FloatProperty(
        name='Angle 1',
        default=0
    )

    trajectory_angle2: FloatProperty(
        name='Angle 2',
        default=0
    )

    trajectory_fouling1: StringProperty(
        name='Fouling 1',
        default=""
    )

    trajectory_fouling2: StringProperty(
        name='Fouling 2',
        default=""
    )

    trajectory_vradius: FloatProperty(
        name='Vertical Radius',
        default=0
    )

    trajectory_railprofile: StringProperty(
        name='Rail Profile',
        default=""
    )

    trajectory_friction_memcell_name: StringProperty(
        name="Friction Memcell",
        default=""
    )

    include_file: StringProperty(
        name="*.inc file",
        subtype='FILE_PATH',
    )
    
    

class SCNObjectPropertiesPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_scn"
    bl_label = "SCN Object"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "[EU07] SCN Editor"

    @classmethod
    def poll(self, context):
        return context.object is not None

    def draw(self, context):
        self.obj = context.object

        type_r = self.layout.row()
        type_r.prop(self.obj.scn_properties, "type_")

        if ("node:" in self.obj.scn_properties.type_):
            maxdistance_r = self.layout.row()
            maxdistance_r.prop(self.obj.scn_properties, "node_max_distance")

            mindistance_r = self.layout.row()
            mindistance_r.prop(self.obj.scn_properties, "node_min_distance")

        if ("node:track" in self.obj.scn_properties.type_):
            if (self.obj.type != 'CURVE'):
                self.layout.label(text="Trajectory must be a Curve!")
            else:
                profile_instance = trajectory_utils.get_profile_instance(self.obj)

                width_r = self.layout.row()
                width_r.prop(self.obj.scn_properties, "trajectory_width")

                box = self.layout.box()
                box.label(text="Profile:")
                box.row().prop(self.obj.scn_properties, "trajectory_profile_param1")
                box.row().prop(self.obj.scn_properties, "trajectory_profile_param2")
                box.row().prop(self.obj.scn_properties, "trajectory_profile_param3")

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

                event0_r = self.layout.row()
                event0_r.prop(self.obj.scn_properties, "trajectory_event0")

                event1_r = self.layout.row()
                event1_r.prop(self.obj.scn_properties, "trajectory_event1")

                event2_r = self.layout.row()
                event2_r.prop(self.obj.scn_properties, "trajectory_event2")

                eventall0_r = self.layout.row()
                eventall0_r.prop(self.obj.scn_properties, "trajectory_eventall0")

                eventall1_r = self.layout.row()
                eventall1_r.prop(self.obj.scn_properties, "trajectory_eventall1")

                eventall2_r = self.layout.row()
                eventall2_r.prop(self.obj.scn_properties, "trajectory_eventall2")

                isolated_r = self.layout.row()
                isolated_r.prop(self.obj.scn_properties, "trajectory_isolated")

                overhead_r = self.layout.row()
                overhead_r.prop(self.obj.scn_properties, "trajectory_overhead")

                angle1_r = self.layout.row()
                angle1_r.prop(self.obj.scn_properties, "trajectory_angle1")

                angle2_r = self.layout.row()
                angle2_r.prop(self.obj.scn_properties, "trajectory_angle2")

                fouling1_r = self.layout.row()
                fouling1_r.prop(self.obj.scn_properties, "trajectory_fouling1")

                fouling2_r = self.layout.row()
                fouling2_r.prop(self.obj.scn_properties, "trajectory_fouling2")

                vradius_r = self.layout.row()
                vradius_r.prop(self.obj.scn_properties, "trajectory_vradius")

                railprofile_r = self.layout.row()
                railprofile_r.prop(self.obj.scn_properties, "trajectory_railprofile")

                friction_memcell_name_r = self.layout.row()
                friction_memcell_name_r.prop(self.obj.scn_properties, "trajectory_friction_memcell_name")

                for i in range(2):
                    mrow = self.layout.row()
                    mrow.prop(profile_instance.material_slots[i], "material")
                    mrow.operator('import_material.mat', icon='PLUS', text="")
                    op = mrow.operator('scn.copy_materials_to_selected', text="Copy To Selected")
                    op.index = i



class CopyMaterialsToSelectedOperator(bpy.types.Operator):
    bl_idname = "scn.copy_materials_to_selected"
    bl_label = "Copy Materials To Selected"

    index: IntProperty()

    def execute(self, context):
        active = context.active_object

        if ("node:track" in active.scn_properties.type_):

            for o in context.selected_objects:
                if ("node:track" in o.scn_properties.type_):
                    trajectory_utils.set_material(o, trajectory_utils.get_material(active, self.index), self.index)

        return {'FINISHED'}


class AddTrackOperator(bpy.types.Operator):
    bl_idname = "scn.add_track"
    bl_label = "Add Track"

    to_point: IntProperty(
        name="To Point",
        default=1,
        max=2,
        min=1
    )

    def execute(self, context):
        active_trajectory = context.active_object

        new_trajectory = trajectory_utils.create("track", bpy.context.scene.cursor.location)






