import pathlib

import bpy

from common.utils import get_environment_path
import eu07_tools

from e3d.input import E3DImporter
from t3d.input import T3DImporter


class ModelSkinData(bpy.types.PropertyGroup):
    skin_id: bpy.props.IntProperty(
        name="Skin ID",
        min=-4,
        max=-1,
    )

    material_index: bpy.props.IntProperty(
        name="Material index",
        min=0,
    )


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

            for material_slot in objects[0].material_slots:
                is_skinslot = material_slot.material and "replacableskin" in material_slot.material.name
                if is_skinslot:
                    skins = model.mesh.eu07_scn_model_skins
                    skin = skins.add()
                    skin.material_index = material_slot.slot_index
                    skin.skin_id = int(material_slot.material.name[-3:-1])

            bpy.data.objects.remove(objects[0])

        return model



    def get_by_relpath(self, relpath, load_if_missing=False):
        for model in self.models:
            if model.relpath == relpath:
                return model

        if load_if_missing:
            return self.load_from_relpath(relpath)

        return None

classes = (
    ModelSkinData,
    Model,
    ModelBank
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.eu07_scn_model_bank = bpy.props.PointerProperty(type=ModelBank)
    bpy.types.Mesh.eu07_scn_model_skins = bpy.props.CollectionProperty(type=ModelSkinData)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.eu07_scn_model_bank
