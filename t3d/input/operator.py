import pathlib

import bpy
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper

import eu07_tools
from common.utils import get_root

from t3d.input.importer import T3DImporter


class T3DImportOperator(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.t3d"
    bl_label = "Import T3D"
    filename_ext = ".t3d"

    filter_glob: StringProperty(
        default="*.t3d",
        options={'HIDDEN'}
    )
    load_includes: BoolProperty(
        name="Load includes",
        default=True,
    )
    import_meshes: BoolProperty(
        name="Import Meshes",
        default=True,
    )
    import_spots: BoolProperty(
        name="Import FreeSpotLights",
        default=True
    )
    import_stars: BoolProperty(
        name="Import Stars",
        default=True
    )

    def execute(self, context):
        root = get_root(self.filepath)
        basedir = pathlib.Path(self.filepath).parent
        asset_searcher = eu07_tools.utils.AssetSearcher(root, basedir)
        asset_searcher.models.remove_extension(".e3d")

        importer = T3DImporter(asset_searcher)
        importer.load_includes = self.load_includes
        importer.import_meshes = self.import_meshes
        importer.import_spots = self.import_spots
        importer.import_stars = self.import_stars

        objects = importer.import_from_filepath(self.filepath)

        for obj in objects:
            bpy.context.scene.collection.objects.link(obj)

        return {'FINISHED'}