import collections

import bpy
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ExportHelper

from ...common import get_root
from .output_builders import export_model


class T3DExporter(bpy.types.Operator, ExportHelper):
    bl_idname = "export_scene.t3d"
    bl_label = "Export T3D"
    filename_ext = ".t3d"

    filter_glob: StringProperty(
        default="*.t3d",
        options={'HIDDEN'}
    )
    use_selection: BoolProperty(
        name="Selection Only",
        default=False
    )
    export_include_collections: BoolProperty(
        name="Export include collections",
        default = True
    )
    use_modifiers: BoolProperty(
        name="Apply modifiers",
        default=True
    )
    use_indices: BoolProperty(
        name="Export face indices",
        default=False
    )
    namespace_prefix: StringProperty(
        name="Namespace prefix",
        default=""
    )

    def execute(self, context):
        Config = collections.namedtuple(
            "Config",
            "root use_selection export_include_collections use_modifiers use_indices namespace_prefix"
        )

        config = Config(
            get_root(self.filepath),
            self.use_selection,
            self.export_include_collections,
            self.use_modifiers,
            self.use_indices,
            self.namespace_prefix
        )

        collection = bpy.context.scene.collection

        with open(self.filepath, "w+", encoding="windows-1250", newline="\r\n") as file:
            export_model(collection, file, config)

        return {'FINISHED'}