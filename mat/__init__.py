from pathlib import Path

from bpy_extras.io_utils import ImportHelper
import bpy
from bpy.props import StringProperty, BoolProperty

import eu07_tools
from ..common import get_root


class EU07MaterialImporter(bpy.types.Operator, ImportHelper):
    bl_idname = "import_material.mat"
    bl_label = "Import MAT"

    filter_glob: StringProperty(
        default="*.mat",
        options={'HIDDEN'}
    )

    prevent_duplication: BoolProperty(
        default=False
    )

    def execute(self, context):
        helper_mat_importer = HelperMATImporter()
        helper_mat_importer.import_mat_from_abspath(self.filepath, self.prevent_duplication)

        return {'FINISHED'}

# TODO: Refactor (get rid of staticmethods maybe)
class HelperMATImporter:
    def __init__(self):
        self.bl_mat = None
        self.asset_searcher = None
        self.nodes = None
        self.links = None
        self.bsdf = None

    @staticmethod
    def import_material_from_relpath(self, relpath, prevent_duplication=True):
        asset_searcher = eu07_tools.utils.AssetSearcher(get_root())

        abspath = asset_searcher.textures.find(relpath)
        return HelperMATImporter.import_material_from_abspath(abspath, prevent_duplication)

    @staticmethod
    def import_material_from_abspath(self, filepath, prevent_duplication=True):
        filepath = eu07_tools.utils.lower_filepath_name(filepath)
        if not Path(filepath).exists():
            return

        # NOTE: What a stupid anti-pattern XD
        HelperMATImporter().import_material(filepath, prevent_duplication)

    def import_material(self, filepath, prevent_duplication=True):
        if prevent_duplication:
            root = get_root(filepath)
            mat_name = str(Path(filepath).relative_to(Path(root)).with_suffix(""))

            duplicate_candidate = bpy.data.materials.get(mat_name)
            if duplicate_candidate:
                return duplicate_candidate

        self.bl_mat = bpy.data.materials.new(mat_name)
        self.bl_mat.use_nodes = True
        self.bl_mat.use_backface_culling = True
        self.bl_mat.blend_method = 'CLIP'

        self.nodes = self.bl_mat.node_tree.nodes
        self.links = self.bl_mat.node_tree.links
        self.bsdf = self.nodes.get("Principled BSDF")

        self.bsdf.inputs["Specular"].default_value = 0
        self.bsdf.inputs["Roughness"].default_value = 1

        self.asset_searcher = eu07_tools.utils.AssetSearcher(
            root, Path(filepath).parent
        )

        if filepath.endswith(".mat"):
            with open(filepath, encoding="latin-1") as matfile:
                eu07_mat = eu07_tools.mat.load(matfile)
                self.nodify_mat_mapping(eu07_mat)
        else: # standalone texture
            self._import_texture(filepath, "texture_diffuse")
            
        return self.bl_mat


    def _import_texture(self, relpath, node_name, parent=None):
        self.asset_searcher.textures.remove_extension(".mat")

        tex_path = self.asset_searcher.textures.find(relpath.split(":")[0])

        if tex_path:

            img_node = self.nodes.new("ShaderNodeTexImage")
            img_node.name = node_name
            img_node.label = node_name
            img_node.parent = parent

            if tex_path.endswith(".dds"):
                img_node.texture_mapping.scale[1] = -1

            img_node.image = bpy.data.images.load(tex_path, check_existing=True)

            if node_name == "texture_normalmap":
                img_node.image.colorspace_settings.name = 'Non-Color'
                normal_map_node = self.nodes.new("ShaderNodeNormalMap")
                normal_map_node.parent = parent
                
                self.links.new(img_node.outputs[0], normal_map_node.inputs[1])

                # NOTE: Normal maps look kinda bad so i disabled link to shader slot.
                if not parent and False:
                    self.links.new(normal_map_node.outputs[0], self.nodes.get("Principled BSDF").inputs[self.NORMAL_INPUT])

            elif node_name == "texture_diffuse" and not parent:
                self.links.new(img_node.outputs[0], self.bsdf.inputs["Base Color"])
                self.links.new(img_node.outputs[1], self.bsdf_inputs["Alpha"])

        self.asset_searcher.textures.add_extension(".mat", priority=0)


    def nodify_mat_mapping(self, mapping, parent=None):
        self.add_texture_node_if_present(mapping, "texture_diffuse", parent)
        self.add_texture_node_if_present(mapping, "texture_normalmap", parent)

        for key, value in mapping.items():
            if key in eu07_tools.mat.NUMERIC_KEYS: #or key.startswith("param"):
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
                self._import_texture(texture_object.value, key, parent)

    def _add_node_generic(self, typename, name, parent):
        node = self.nodes.new(typename)
        node.name = self._create_node_name(name, parent)
        node.label = name
        node.parent = parent

        return node

    def _create_node_name(self, name, parent):
        return f"{parent.name}.{name}" if parent else name


