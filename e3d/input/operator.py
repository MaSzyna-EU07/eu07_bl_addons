from pathlib import Path

import bpy
from common.utils import get_environment_path
import eu07_tools
from e3d.input.importer import E3DImporter
from bpy_extras.io_utils import ImportHelper


class E3DImportOperator(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.e3d"
    bl_label = "Import E3D"
    filename_ext = ".e3d"

    filter_glob: bpy.props.StringProperty(
        default="*.e3d",
        options={'HIDDEN'}
    )
    import_meshes: bpy.props.BoolProperty(
        name="Import Meshes",
        default=True,
    )
    import_spots: bpy.props.BoolProperty(
        name="Import FreeSpotLights",
        default=True
    )
    import_stars: bpy.props.BoolProperty(
        name="Import Stars",
        default=True
    )

    def execute(self, context):
        asset_searcher = eu07_tools.utils.AssetSearcher(
            get_environment_path(self.filepath),
            Path(self.filepath).parent
        )

        importer = E3DImporter(asset_searcher)
        importer.import_meshes = self.import_meshes
        importer.import_spots = self.import_spots
        importer.import_stars = self.import_stars

        objects = importer.import_from_filepath(self.filepath)

        for obj in objects:
            bpy.context.scene.collection.objects.link(obj)

        return {'FINISHED'}
