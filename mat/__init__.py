from pathlib import Path

from bpy_extras.io_utils import ImportHelper
import bpy

from eu07_tools import mat

class MATImport(bpy.types.Operator, ImportHelper):
    bl_idname = "import_material.mat"
    bl_label = "Import MAT"
    filename_ext = ".mat"

    def execute(self, context):
        root = self.filepath[:self.filepath.index("textures")]

        matpath = Path(self.filepath).relative_to(Path(root, "textures"))
        self.bl_mat = bpy.data.materials.new(matpath) 

        eu07_mat = mat.load(self.filepath)

    def _make_node_tree(self, eu07_mat):
        tree = self.bl_mat.node_tree

        