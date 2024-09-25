import bpy
from bpy_extras.io_utils import ExportHelper

from .exporter import T3DExporter


class EU07_OT_ExportT3D(bpy.types.Operator, ExportHelper):
    bl_idname = "export_scene.t3d"
    bl_label = "Export T3D"
    filename_ext = ".t3d"

    filter_glob: bpy.props.StringProperty(
        default="*.t3d",
        options={'HIDDEN'}
    )
    objects_range: bpy.props.EnumProperty(
        name="Export range",
        items=[
            ("ALL", "All Objects", "Export all objects from scene"),
            ("SELECTION", "Selected Objects", "Export only selected objects"),
            ("VISIBLE", "Visible Objects", "Export only visible objects"),
            ("ACTIVE_COLLECTION", "Active Collection", "Export objects from active collection"),
        ]
    )
    apply_modifiers: bpy.props.BoolProperty(
        name="Apply modifiers",
        default=True,
        description="Export mesh_data with applied modifiers"
    )
    aggregate_includes: bpy.props.BoolProperty(
        name="Aggregate includes",
        default=False,
        description="Write all include objects to main file - do not write into include files",
        options={'HIDDEN'}
    )
    embed_skins: bpy.props.BoolProperty(
        name="Embed skins",
        default=False,
        description="Export material paths instead replaceable skins identifiers",
        options={'HIDDEN'}
    )
    remove_name_suffixes: bpy.props.BoolProperty(
        name="Remove name suffixes",
        default=False,
        description="Remove .00x suffixes from object names",
    )

    use_generated_img_name: bpy.props.BoolProperty(
        default=False,
        options={'HIDDEN'}
    )

    def execute(self, context):
        exporter = T3DExporter()
        exporter.objects_range = self.objects_range
        exporter.apply_modifiers = self.apply_modifiers
        exporter.aggregate_includes = self.aggregate_includes
        exporter.embed_skins = self.embed_skins
        exporter.remove_name_suffixes = self.remove_name_suffixes
        exporter.use_generated_img_name = self.use_generated_img_name

        exporter.export_to_file(self.filepath)

        return {'FINISHED'}

class EU07_FH_t3d_export(bpy.types.FileHandler):
    bl_idname = "EU07_FH_t3d_import"
    bl_label = "File handler for T3D model import"
    bl_import_operator = 'collection'
    bl_file_extensions = ".t3d"

