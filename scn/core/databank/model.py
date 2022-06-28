import pathlib

import bpy

from common.utils import get_environment_path
import eu07_tools

from e3d.input import E3DImporter
from t3d.input import T3DImporter

class Model(bpy.types.PropertyGroup):
    relpath: bpy.props.StringProperty()

    mesh: bpy.props.PointerProperty(
        type=bpy.types.Mesh
    )


class ModelBank(bpy.types.PropertyGroup):
    models: bpy.props.CollectionProperty(
        type=Model
    )

    def load_from_relpath(self, relpath):
        environment_path = get_environment_path()
        asset_searcher = eu07_tools.utils.AssetSearcher(environment_path)

        fullpath = asset_searcher.models.find(relpath)

        if fullpath.endswith(".e3d"):
            importer = E3DImporter(asset_searcher)
        elif fullpath.endswith(".t3d"):
            importer = T3DImporter(asset_searcher)
            importer.load_included_objects = True
            importer.import_stars = False
            importer.import_spots = False
            importer.join_to_one_mesh = True
        else:
            pass


