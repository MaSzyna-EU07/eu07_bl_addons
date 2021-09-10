import collections
from pathlib import Path

import bpy
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
import eu07_tools

from ...common import get_root
from .input_builders import import_model


class T3DImporter(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.t3d"
    bl_label = "Import T3D"
    filename_ext = ".t3d"

    filter_glob: StringProperty(
        default="*.t3d",
        options={'HIDDEN'}
    )
    skin_1: StringProperty(
        name="Skin #1",
    )
    skin_2: StringProperty(
        name="Skin #2",
    )
    skin_3: StringProperty(
        name="Skin #3",
    )
    skin_4: StringProperty(
        name="Skin #4",
    )
    load_includes: BoolProperty(
        name="Load included submodels",
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
    merge_all: BoolProperty(
        name="Merge to single mesh",
        default=False,
        options={'HIDDEN'}
    )
    link_merged_object: BoolProperty(
        name="Link merged object to scene collection",
        default=True,
        options={'HIDDEN'}
    )

    def execute(self, context):
        Config = collections.namedtuple(
            "Config",
            "report_func root skins asset_searcher load_includes import_meshes import_spots import_stars merge_all"
        )

        skins = {
            "replacableskin": self.skin_1,
            "-1": self.skin_1,
            "-2": self.skin_2,
            "-3": self.skin_3,
            "-4": self.skin_4,
        }

        root = get_root(self.filepath)

        asset_searcher = eu07_tools.utils.AssetSearcher(
            root,
            Path(self.filepath).parent
        )

        config = Config(
            self.report, root, skins, asset_searcher,
            self.load_includes, self.import_meshes, self.import_spots, self.import_stars,
            self.merge_all
        )

        collection = bpy.context.scene.collection

        with open(self.filepath, "r", encoding="latin-1") as file:
            elements = eu07_tools.t3d.load(file)
            imported = import_model(elements, collection, config)

            if self.merge_all:
                name = str(Path(self.filepath).with_suffix("").relative_to(root))
                named_mesh = bpy.data.meshes.new(name)
                named_obj = bpy.data.objects.new(name, named_mesh)
                if self.link_merged_object:
                    bpy.context.scene.collection.objects.link(named_obj)

                named_obj.select_set(True)

                for imported_object in imported:
                    if imported_object.type == 'MESH':
                        imported_object.select_set(True)

                context.view_layer.objects.active = ob = named_obj

                bpy.ops.object.join()

        return {'FINISHED'}