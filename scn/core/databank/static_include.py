import eu07_tools
from common import get_environment_path
from eu07_tools.utils import AssetSearcher
from inc.input import INCImporter


class StaticIncludeBankRecord(bpy.types.PropertyGroup):
    relpath: bpy.props.StringProperty()

    params_string: bpy.props.StringProperty()

    mesh: bpy.props.PointerProperty(
        type=bpy.types.Mesh
    )


class StaticIncludeBank(bpy.types.PropertyGroup):
    records: bpy.props.CollectionProperty(
        type=StaticIncludeBankRecord
    )

    def load_from_relpath(self, relpath, params_string):
        root = get_environment_path()
        asset_searcher = AssetSearcher(root)
        importer = INCImporter(asset_searcher)
        importer.join_into_one = True
        importer.parameters = params_string.split(" ")

        full_path = asset_searcher.scenes.find(relpath)

        objects = importer.import_from_filepath(full_path)

        if objects:
            record = self.records.add()
            record.relpath = relpath
            record.params_string = params_string
            record.mesh = objects[0].data

            return record


    def get(self, relpath, params_string):
        for record in self.records:
            if record.relpath == relpath and record.params_string == params_string:
                return record