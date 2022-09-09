import pathlib

import bpy
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper

import eu07_tools
from common.utils import get_environment_path

from inc.input.importer import INCImporter



class INCImportOperator(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.inc"
    bl_label = "Import INC"
    filename_ext = ".inc"

    filter_glob: StringProperty(
        default="*.inc",
        options={'HIDDEN'}
    )
    parameters_string: StringProperty(
        name="Parameters string",
        default=""
    )

    join_into_one: BoolProperty(
        name="Join to one mesh",
        default=False,
        #options={'HIDDEN'}
    )

    def execute(self, context):
        root = get_environment_path(self.filepath)
        basedir = pathlib.Path(self.filepath).parent
        asset_searcher = eu07_tools.utils.AssetSearcher(root, basedir)

        importer = INCImporter(asset_searcher)
        importer.join_into_one = self.join_into_one
        importer.parameters = self.parameters_string.strip().split(" ")

        objects = importer.import_from_filepath(self.filepath)

        for obj in objects:
            bpy.context.scene.collection.objects.link(obj)

        return {'FINISHED'}