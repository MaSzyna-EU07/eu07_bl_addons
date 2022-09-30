import bpy
from bpy_extras.io_utils import ExportHelper

from material_tools.output.exporter import MaterialExporter


class EU07_OT_ExportMAT(bpy.types.Operator, ExportHelper):
    bl_idname = "eu07.export_material"
    bl_label = "Export MAT"
    filename_ext = ".mat"

    filter_glob: bpy.props.StringProperty(
        default="*.mat",
        options={'HIDDEN'}
    )

    def execute(self, context):
        exporter = MaterialExporter()
        if context.active_object:
            if context.active_object.active_material:
                with open(self.filepath, "w+", encoding="windows-1250", newline="\r\n") as f:
                    exporter.export_to_file(f, context.active_object.active_material.eu07_material)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(EU07_OT_ExportMAT)


def unregsiter():
    bpy.utils.unregister_class(EU07_OT_ExportMAT)