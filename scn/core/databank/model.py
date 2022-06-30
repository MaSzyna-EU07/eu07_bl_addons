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

        importer = None
        if fullpath.endswith(".e3d"):
            importer = E3DImporter(asset_searcher)
            importer.import_stars = False
            importer.import_spots = False
            importer.join_into_one = True
            importer.import_lod = False

        elif fullpath.endswith(".t3d"):
            importer = T3DImporter(asset_searcher)
            importer.load_included_objects = True
            importer.import_stars = False
            importer.import_spots = False
            importer.join_into_one = True
            importer.import_lod = False
        else:
            pass

        if importer is None:
            return

        objects = importer.import_from_filepath(fullpath)

        if objects:
            model = self.models.add()
            model.relpath = relpath
            model.name = relpath
            model.mesh = objects[0].data
            model.mesh.name = relpath

            objects[0].data.use_fake_user = True
            bpy.data.objects.remove(objects[0])

        return model


classes = (
    Model,
    ModelBank
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.eu07_scn_model_bank = bpy.props.PointerProperty(type=ModelBank)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.eu07_scn_model_bank
