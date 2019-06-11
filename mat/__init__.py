from pathlib import Path

from bpy_extras.io_utils import ImportHelper
import bpy

from eu07_tools import mat
from eu07_tools.utils import find_root

class MATImport(bpy.types.Operator, ImportHelper):
    bl_idname = "import_material.mat"
    bl_label = "Import MAT"
    filename_ext = ".mat"

    def execute(self, context):
        root = find_root(self.filepath)

        matpath = str(Path(self.filepath).relative_to(Path(root, "textures")))
        self.bl_mat = bpy.data.materials.new(matpath)
        self.bl_mat.use_nodes = True

        self.nodes = self.bl_mat.node_tree.nodes
        self.links = self.bl_mat.node_tree.links

        eu07_mat = mat.load(open(self.filepath))
        print(eu07_mat)
        self.nodify_mat_mapping(eu07_mat)

        return {'FINISHED'}

    def nodify_mat_mapping(self, mapping, parent=None):
        print("---- next call")
        print(mapping)
        self.add_texture_node_if_present(mapping, "texture_diffuse", parent)
        self.add_texture_node_if_present(mapping, "texture_normal", parent)

        for key, value in mapping.items():
            if key.startswith("param_"):
                self.add_value_node_if_present(mapping, key, parent)

            elif key in mat.NESTED_MAPPING_KEYS:
                frame = self.nodes.new("NodeFrame")
                frame.name = self._create_node_name(key, frame)
                frame.label = key
                self.nodify_mat_mapping(value, frame)

    def add_value_node_if_present(self, mapping, key, parent):
        if key in mapping:
            node = self.nodes.new("ShaderNodeValue")
            node.name = self._create_node_name(key, parent)
            node.label = key
            node.parent = parent

    def add_texture_node_if_present(self, mapping, key, parent):
        if key in mapping:
            node = self.nodes.new("ShaderNodeTexImage")
            node.name = self._create_node_name(key, parent)
            node.label = key
            node.parent = parent

    def _create_node_name(self, name, parent):
        return f"{parent.name}.{name}" if parent else name






        