import pathlib

import bpy
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper

import eu07_tools
from common.utils import get_environment_path

from t3d.input.importer import T3DImporter

import cProfile


class T3DImportOperator(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.t3d"
    bl_label = "Import T3D"
    filename_ext = ".t3d"

    filter_glob: StringProperty(
        default="*.t3d",
        options={'HIDDEN'}
    )
    load_included_objects: BoolProperty(
        name="Load Included Objects",
        default=True,
    )
    import_meshes: BoolProperty(
        name="Import Meshes",
        default=True,
        options={'HIDDEN'}
    )
    import_spots: BoolProperty(
        name="Import FreeSpotLights",
        default=True,
        options={'HIDDEN'}
    )
    import_stars: BoolProperty(
        name="Import Stars",
        default=True,
        options={'HIDDEN'}
    )

    def execute(self, context):
        root = get_environment_path(self.filepath)
        basedir = pathlib.Path(self.filepath).parent
        asset_searcher = eu07_tools.utils.AssetSearcher(root, basedir)
        asset_searcher.models.remove_extension(".e3d")

        importer = T3DImporter(asset_searcher)
        importer.load_included_objects = self.load_included_objects
        importer.import_meshes = self.import_meshes
        importer.import_spots = self.import_spots
        importer.import_stars = self.import_stars

        objects = importer.import_from_filepath(self.filepath)

        return {'FINISHED'}