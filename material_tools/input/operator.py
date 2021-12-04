from pathlib import Path

import bpy
from bpy_extras.io_utils import ImportHelper

import eu07_tools
from common import get_root
from .importer import MATImporter

class EU07_OT_MaterialImport(bpy.types.Operator, ImportHelper):
    bl_idname = "eu07.import_material"
    bl_label = "Import material"

    filter_glob: bpy.props.StringProperty(
        default="*.mat;*.tga;*.dds;*.png;*.bmp",
        options={'HIDDEN'}
    )
    files: bpy.props.CollectionProperty(
        name="File Path",
        type=bpy.types.OperatorFileListElement,
    )
    directory: bpy.props.StringProperty(
        subtype='DIR_PATH',
    )
    use_fake_user: bpy.props.BoolProperty(
        name="Use fake user",
        default=False
    )
    import_into_active: bpy.props.BoolProperty(
        name="Import into active",
        default=False,
        options={'HIDDEN'}
    )
    set_new_as_active: bpy.props.BoolProperty(
        name="Set new as active",
        default=False,
        options={'HIDDEN'}
    )


    filename_ext = ""

    def execute(self, context):
        active_material = bpy.context.active_object.active_material if self.import_into_active else None

        directory = self.directory
        for file_elem in self.files:
            filepath = str(Path(directory, file_elem.name))
            asset_searcher = eu07_tools.utils.AssetSearcher(
                get_root(filepath), Path(filepath).parent
            )
            importer = MATImporter(asset_searcher)
            material = importer.import_from_abspath(filepath, active_material)
            importer.use_fake_user = self.use_fake_user

            if not self.import_into_active and self.set_new_as_active:
                if context.active_object:
                    context.active_object.active_material = material

        return {'FINISHED'}