from datetime import datetime
import pathlib

import bpy
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ExportHelper
import eu07_tools

from common.export_manager import ExportManager
from common import utils


class SCNExporter(bpy.types.Operator, ExportHelper):
    bl_idname = "export_scene.scn"
    bl_label = "Export SCN"
    filename_ext = ".scn"

    filter_glob: StringProperty(
        default="*.scn;*.scm;*.inc",
        options={'HIDDEN'}
    )
    use_selection: BoolProperty(
        name="Use selection",
        default=False
    )

    def execute(self, context):
        export_manager = ExportManager(bpy.context.scene.eu07_includes)
        export_manager.create_buffers()
        export_manager.create_outputs(eu07_tools.scn.SCNOutput)

        for buffer in export_manager.buffers:
            export_date = datetime.now().strftime("%d/%m/%Y %H:%M")
            buffer.write(f"// Exported from BlendSCN Editor {export_date}\n\n")

        # export_manager.master_output.dump_element(config.get_config_as_element())

        for include in bpy.context.scene.eu07_includes:
            include_element = eu07_tools.scn.create_element("include")
            include_element.path = str(pathlib.Path(include.file_path).relative_to("scenery"))

            export_manager.master_output.dump_element(include_element)

        export_manager.master_buffer.write("\n")

        if self.use_selection:
            objects = [o for o in bpy.data.objects if o.select_get()]
        else:
            objects = bpy.data.objects

        for obj in objects:
            print(f"Exporting {obj} to SCN")
            output = export_manager.get_output(obj.eu07_include_identifier)

            element = self._create_element_from_object(obj)
            output.dump_element(element)

        # export_manager.master_buffer.write(firstinit.get_firstinit())

        export_manager.flush_buffers_to_files(utils.get_environment_path(), self.filepath)

        return {'FINISHED'}

    def _create_element_from_object(self, obj):
        element = None
        if "node:track" in obj.eu07_scn_entity_type:
            element = self._create_node_track(obj)

        return element

    def _create_node_track(self, obj):
        track = eu07_tools.scn.create_element("node:track")

        tp = obj.eu07_track

        track.name = tp.name
        track.max_distance = tp.max_distance
        track.min_distance = tp.min_distance
        track.subtype = tp.type
        track.length = tp.length
        track.width = tp.width
        track.friction = tp.friction
        track.sound_distance = tp.sound_distance
        track.quality_flag = tp.quality_flag
        track.damage_flag = tp.damage_flag
        track.environment = tp.environment
        track.visible = tp.visibility
        track.map1 = "none"
        track.map2 = "none"
        track.mapping_length = tp.map1_length
        track.geometry_params = tp.geometry_params

        track.p1 = tp.p1
        track.p1_roll = tp.p1_roll
        track.cv1 = tp.get_cv1_local()
        track.cv2 = tp.get_cv2_local()
        track.p2 = tp.p2
        track.p2_roll = tp.p2_roll
        track.radius1 = tp.radius1

        track.p3 = tp.p3
        track.p3_roll = tp.p3_roll
        track.cv3 = tp.get_cv3_local()
        track.cv4 = tp.get_cv4_local()
        track.p4 = tp.p4
        track.p4_roll = tp.p4_roll
        track.radius2 = tp.radius2

        track.velocity = tp.velocity
        track.event0 = tp.event0_name
        track.event1 = tp.event1_name
        track.event2 = tp.event2_name
        track.eventall0 = tp.eventall0_name
        track.eventall1 = tp.eventall1_name
        track.eventall2 = tp.eventall2_name
        track.isolated = tp.isolated_name
        track.overhead = tp.overhead
        track.angle1 = tp.angle1
        track.angle2 = tp.angle2
        track.fouling1 = tp.fouling1
        track.fouling2 = tp.fouling2
        track.railprofile = tp.railprofile
        track.friction_memcell_name = tp.friction_memcell
        track.trackbed = "none"

        return track

