import bpy
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ExportHelper

from .exporter import T3DExporter


class EU07_OT_ExportT3D(bpy.types.Operator, ExportHelper):
    bl_idname = "export_scene.t3d"
    bl_label = "Export T3D"
    filename_ext = ".t3d"

    filter_glob: StringProperty(
        default="*.t3d",
        options={'HIDDEN'}
    )
    use_selection: BoolProperty(
        name="Selection Only",
        default=False
    )
    apply_modifiers: BoolProperty(
        name="Apply modifiers",
        default=True
    )

    def execute(self, context):
        exporter = T3DExporter()
        exporter.use_selection = self.use_selection
        exporter.apply_modifiers = self.apply_modifiers

        exporter.export_to_file(self.filepath)

        return {'FINISHED'}





