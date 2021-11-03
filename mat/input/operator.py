from pathlib import Path

import bpy
from bpy_extras.io_utils import ImportHelper

import eu07_tools
from common import get_root
from .importer import MATImporter

class MATImportOperator(bpy.types.Operator, ImportHelper):
    bl_idname = "import_material.mat"
    bl_label = "Import material"

    filter_glob: bpy.props.StringProperty(
        default="*.mat;*.tga;*.dds;*.png",
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

    filename_ext = ""

    def execute(self, context):
        directory = self.directory
        for file_elem in self.files:
            filepath = str(Path(directory, file_elem.name))
            asset_searcher = eu07_tools.utils.AssetSearcher(
                get_root(filepath), Path(filepath).parent
            )
            importer = MATImporter(asset_searcher)
            importer.import_from_abspath(filepath)
            importer.use_fake_user = self.use_fake_user

        return {'FINISHED'}