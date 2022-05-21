import bpy
from bpy_extras.io_utils import ExportHelper

from .exporter import AnimationExporter


class EU07_OT_ExportAnimation(bpy.types.Operator, ExportHelper):
    bl_idname = "eu07.anim_export"
    bl_label = "Export Animation Events"
    filename_ext = ".ctr"

    filter_glob: bpy.props.StringProperty(
        default="*.ctr",
        options={'HIDDEN'}
    )

    objects_range: bpy.props.EnumProperty(
        name="Export range",
        items=[
            ("ALL", "All Objects", "Export animation from all objects"),
            ("SELECTION", "Selected Objects", "Export animation only from selected objects"),
            ("VISIBLE", "Visible Objects", "Export animation only from visible objects"),
            ("ACTIVE_COLLECTION", "Active Collection", "Export animation only from objects in active collection"),
        ]
    )

    model_name: bpy.props.StringProperty(
        name="Node Model name",
        default="",
    )

    main_event_name: bpy.props.StringProperty(
        name="Main event name",
        default="",
    )

    def execute(self, context):
        exporter = AnimationExporter()
        exporter.objects_range = self.objects_range
        exporter.model_name = self.model_name
        exporter.main_event_name = self.main_event_name

        exporter.export_to_filepath(self.filepath)

        return {'FINISHED'}





