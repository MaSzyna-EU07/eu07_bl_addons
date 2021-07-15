from pathlib import Path

from bpy_extras.io_utils import ImportHelper
import bpy
from bpy.props import StringProperty

import eu07_tools

from ..common import get_root

class MATImport(bpy.types.Operator, ImportHelper):
    bl_idname = "import_material.mat"
    bl_label = "Import MAT"
    filename_ext = ".mat"

    filter_glob: StringProperty(
        default="*.mat",
        options={'HIDDEN'}
    )

    def execute(self, context):
        root = get_root(self.filepath)

        self.asset_searcher = eu07_tools.utils.AssetSearcher(
            root, Path(self.filepath).parent
        )
        self.asset_searcher.textures.remove_extension(".mat")

        mat_name = "[MAT]" + str(Path(self.filepath).relative_to(Path(root, "textures")))
        self.bl_mat = bpy.data.materials.new(mat_name)
        self.bl_mat.use_nodes = True

        self.nodes = self.bl_mat.node_tree.nodes
        self.links = self.bl_mat.node_tree.links

        eu07_mat = eu07_tools.mat.load(open(self.filepath))
        self.nodify_mat_mapping(eu07_mat)

        return {'FINISHED'}


    def nodify_mat_mapping(self, mapping, parent=None):
        self.add_texture_node_if_present(mapping, "texture_diffuse", parent)
        self.add_texture_node_if_present(mapping, "texture_normalmap", parent)

        for key, value in mapping.items():
            if key.startswith("param") or key in eu07_tools.mat.NUMERIC_KEYS:
                node = self.add_value_node_if_present(mapping, key, parent)
                node.outputs[0].default_value = mapping[key]

            if key.startswith("size"):
                size = mapping[key]

                node_x = self._add_node_generic("ShaderNodeValue", "size(x)", parent)
                node_x.outputs[0].default_value = size[0]

                node_y = self._add_node_generic("ShaderNodeValue", "size(y)", parent)
                node_y.outputs[0].default_value = size[1]

            elif key in eu07_tools.mat.NESTED_MAPPING_KEYS:
                frame = self.nodes.new("NodeFrame")
                frame.name = key
                frame.name = self._create_node_name(key, frame)
                frame.label = key
                frame.parent = parent
                self.nodify_mat_mapping(value, frame)


    def add_value_node_if_present(self, mapping, key, parent):
        if key not in mapping:
            return

        node = self._add_node_generic("ShaderNodeValue", key, parent)
        return node

    def add_texture_node_if_present(self, mapping, key, parent):
        if key not in mapping:
            return

        node = self._add_node_generic("ShaderNodeTexImage", key, parent)

        if node:
            texture_object = mapping[key]

            if texture_object.value_type == "TEXTURE_PATH":
                tex_path = self.asset_searcher.textures.find(texture_object.value)
                image = bpy.data.images.load(tex_path)

                node.image = image

                if key == "texture_normalmap":
                    node.image.colorspace_settings.name = 'Non-Color'
                    normal_map_node = self.nodes.new("ShaderNodeNormalMap")
                    normal_map_node.parent = parent

                    self.links.new(node.outputs[0], normal_map_node.inputs[1])

                    if not parent:
                        self.links.new(normal_map_node.outputs[0], self.nodes.get("Principled BSDF").inputs[-3])

                elif key == "texture_diffuse" and not parent:
                    self.links.new(node.outputs[0], self.nodes.get("Principled BSDF").inputs[0])





    def _add_node_generic(self, typename, name, parent):
        node = self.nodes.new(typename)
        node.name = self._create_node_name(name, parent)
        node.label = name
        node.parent = parent

        return node

    def _create_node_name(self, name, parent):
        return f"{parent.name}.{name}" if parent else name






        