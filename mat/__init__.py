from bpy_extras.io_utils import ImportHelper
import bpy

class MATImport(bpy.types.Operator, ImportHelper):
    bl_idname = "import_material.mat"