import pathlib

import bpy
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper

from ... import eu07_tools
from ...common.utils import get_environment_path

from ...t3d.input.importer import T3DImporter


class EU07_OT_ImportT3D(bpy.types.Operator, ImportHelper):
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
    join_into_one: BoolProperty(
        name="Join to one mesh",
        default=False,
        #options={'HIDDEN'}
    )
    import_lod: BoolProperty(
        name="Import LODs",
        default=True,
        #options={'HIDDEN'}
    )
    name_prefix: StringProperty(
        name="Name Prefix",
        description="Additional name prefix for imported submodels to prevent parenting issues"
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
        importer.join_into_one = self.join_into_one
        importer.import_lod = self.import_lod
        importer.name_prefix = self.name_prefix

        objects = importer.import_from_filepath(self.filepath)

        for obj in objects:
            bpy.context.scene.collection.objects.link(obj)

        return {'FINISHED'}


class EU07_FH_t3d_import(bpy.types.FileHandler):
    bl_idname = "EU07_FH_t3d_import"
    bl_label = "File handler for T3D model import"
    bl_import_operator = EU07_OT_ImportT3D.bl_idname
    bl_file_extensions = ".t3d"

    @classmethod
    def poll_drop(cls, context):
        return (context.region and context.region.type == 'WINDOW'
                and context.area and context.area.ui_type == 'VIEW_3D'
                )