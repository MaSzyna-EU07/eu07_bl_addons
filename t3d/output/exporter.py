import collections
import io

import bpy
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ExportHelper

from ...common import get_root
from .output_builders import export_model
from common import includes


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

        root = get_root(self.filepath)

        config = Config(
            root,
            self.use_selection,
            self.export_include_collections,
            self.use_modifiers,
            self.use_indices,
            self.namespace_prefix
        )

        outfiles = {}
        for include in context.scene.eu07_includes:
            out_path = (root / include.file_path)
            out_dir = out_path.parent
            out_dir.mkdir(parents=True, exist_ok=True)
            outfiles[include.identifier] = self._open_for_writing(out_path)

        outfiles[includes.MASTER_IDENTIFIER] = self._open_for_writing(self.filepath)

        # robimy tyle bufferów, ile plikow
        # dla kazdego buffera robimy export model z odpowiednim parametrem include_identifier
        # dla glownego buffera wpisujemy jeszcze include elements



        with open(self.filepath, "w+", encoding="windows-1250", newline="\r\n") as file:
            export_model(collection, file, config)

        return {'FINISHED'}