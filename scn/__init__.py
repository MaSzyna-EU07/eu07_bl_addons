import bpy
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper
import eu07_tools.scn

from .input_builders import SceneryBuilder

class SCNImport(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.scn"
    bl_label = "Import SCN"

    filter_glob: StringProperty(
        default="*.scn;*.scm;*.inc",
        options={'HIDDEN'}
    )

    def execute(self, context):
        scn_input = eu07_tools.scn.load(open(self.filepath))

        builder = SceneryBuilder()
        builder.run(scn_input)
        
        return {'FINISHED'}

