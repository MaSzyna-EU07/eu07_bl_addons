import bpy
from bpy.props import EnumProperty, FloatProperty, IntProperty, BoolProperty, StringProperty

import scn

from . import trajectory_tools


def update_material_list(self, context):
    items = []
    for mat in bpy.data.materials:
        items.append((mat.name, mat.name, ""))

    return items


def update_visibility(self, context):
    obj = context.active_object

    if obj is None: return

    if obj.scn_properties.type_.startswith("node:track"):
        profile_instance = trajectory_tools.get_profile_instance(obj)
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
            ("node:memcell", "Memory Cell", ""),
            ("node:triangles", "Terrain", ""),
            ("node:lines", "Lines", ""),
            ("origin", "Origin", ""),
            ("camera", "Camera", ""),
            ("include", "Include", ""),
            ("tree", "Tree", "")
        ]
    )

    scm_file_id: IntProperty(
        name="SCM File ID",
        min=-1,
        default=-1,
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
    )

    trajectory_profile_param2: FloatProperty(
        name="Param 2",
        default=0.5,
    )

    trajectory_profile_param3: FloatProperty(
        name="Param 3",
        default=1.3,
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

    camera_use_index: BoolProperty(
        name="Use index",
        default=True
    )

    camera_index: IntProperty(
        name="Index",
        default=0,
        min=0,
        max=9
    )

    sound_path: StringProperty(
        name="Path",
        default="",
        subtype='FILE_PATH'
    )

    memcell_value_text: StringProperty(
        name="Text Value",
        default=""
    )

    memcell_value_first: StringProperty(
        name="1st numeric value",
        default="0"
    )

    memcell_value_second: StringProperty(
        name="2nd numeric value",
        default="0"
    )

    memcell_track_name: StringProperty(
        name="Track name",
        default="none"
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

        if "include" in self.obj.scn_properties.type_:
            filepath_r = self.layout.row()
            filepath_r.prop(self.obj.scn_properties, "include_file")


        if ("node:" in self.obj.scn_properties.type_):
            maxdistance_r = self.layout.row()
            maxdistance_r.prop(self.obj.scn_properties, "node_max_distance")

            mindistance_r = self.layout.row()
            mindistance_r.prop(self.obj.scn_properties, "node_min_distance")

        if "node:sound" in self.obj.scn_properties.type_:
            sound_path_r = self.layout.row()
            sound_path_r.prop(self.obj.scn_properties, "sound_path")

        if "node:memcell" in self.obj.scn_properties.type_:
            value_text_r = self.layout.row()
            value_text_r.prop(self.obj.scn_properties, "memcell_value_text")

            value_1st_r = self.layout.row()
            value_1st_r.prop(self.obj.scn_properties, "memcell_value_first")

            value_2nd_r = self.layout.row()
            value_2nd_r.prop(self.obj.scn_properties, "memcell_value_second")

            track_name_r = self.layout.row()
            track_name_r.prop(self.obj.scn_properties, "track_name")

        if "camera" in self.obj.scn_properties.type_:
            use_index_r = self.layout.row()
            use_index_r.prop(self.obj.scn_properties, "camera_use_index")

            if self.obj.scn_properties.camera_use_index:
                index_r = self.layout.row()
                index_r.prop(self.obj.scn_properties, "camera_index")

                duplicates = scn.camera.get_cameras_with_index(self.obj.scn_properties.camera_index)
                duplicates_names = [cam.name for cam in duplicates]
                duplicates_names.remove(self.obj.name)

                if len(duplicates_names) > 0:
                    warning_r = self.layout.row()
                    warning_r.label(text="Same index in:", icon='ERROR')

                    for name in duplicates_names:
                        name_r = self.layout.row()
                        name_r.label(text=name)


        if "tree" in self.obj.scn_properties.type_:
            height_r = self.layout.row()
            height_r.label(text=f"Height: {round(self.obj.scale[2], 2)}")
            breadth_r = self.layout.row()
            breadth_r.label(text=f"Breadth: {round(self.obj.scale[1], 2)}")
            material_r = self.layout.row()
            material_r.prop(self.obj, "active_material", text="Material")

        if ("node:track" in self.obj.scn_properties.type_):
            if (self.obj.type != 'CURVE'):
                self.layout.label(text="Trajectory must be a Curve!")
            else:
                profile_instance = trajectory_tools.get_profile_instance(self.obj)

                width_r = self.layout.row()
                width_r.prop(self.obj.scn_properties, "trajectory_width")

                # box = self.layout.box()
                # box.label(text="Profile:")
                # box.row().prop(self.obj.scn_properties, "trajectory_profile_param1")
                # box.row().prop(self.obj.scn_properties, "trajectory_profile_param2")
                # box.row().prop(self.obj.scn_properties, "trajectory_profile_param3")
                # box.row().operator('scn.update_trajectory_profile', text="Update Profile")

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
                p1_roll_r.prop(self.obj.data.splines[0].bezier_points[0], "tilt", text="P1 roll")

                p2_roll_r = self.layout.row()
                p2_roll_r.prop(self.obj.data.splines[0].bezier_points[1], "tilt", text="P2 roll")

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
                    trajectory_tools.set_material(o, trajectory_tools.get_material(active, self.index), self.index)

        return {'FINISHED'}