from pathlib import Path

import bpy
from bpy.types import OperatorFileListElement
from bpy.props import StringProperty, CollectionProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
import eu07_tools

from common import get_root, get_qualified_material_name
from mat.nodegroup import instantiate_mat_nodegroup

from .operator import MATImportOperator
from .importer import MATImporter


# TODO: Refactor (get rid of staticmethods maybe)
class HelperMATImporter:
    def __init__(self):
        self.bl_mat = None
        self.asset_searcher = None
        self.nodes = None
        self.links = None
        self.bsdf = None

    @staticmethod
    def import_material_from_relpath(relpath):
        asset_searcher = eu07_tools.utils.AssetSearcher(get_root())

        abspath = asset_searcher.textures.find(relpath)

        if not abspath:
            return None

        return HelperMATImporter.import_material_from_abspath(abspath)

    @staticmethod
    def import_material_from_abspath(filepath):
        if not Path(filepath).exists():
            return

        return HelperMATImporter().import_material(filepath)

    def import_material(self, filepath):
        return
        root = get_root(filepath)
        mat_name = get_qualified_material_name(filepath)

        duplicate_candidate = bpy.data.materials.get(mat_name)
        if duplicate_candidate:
            return duplicate_candidate

        self.bl_mat = bpy.data.materials.new(mat_name)
        self.bl_mat.use_nodes = True
        self.bl_mat.use_backface_culling = True
        self.bl_mat.blend_method = 'CLIP'
        self.bl_mat.node_tree.nodes.clear()

        self.nodes = self.bl_mat.node_tree.nodes
        self.links = self.bl_mat.node_tree.links

        material_output = self.nodes.new("ShaderNodeOutputMaterial")
        self.nodegroup = instantiate_mat_nodegroup(self.nodes)
        self.links.new(self.nodegroup.outputs[0], material_output.inputs[0])

        self.asset_searcher = eu07_tools.utils.AssetSearcher(
            root, Path(filepath).parent
        )

        if filepath.endswith(".mat"):
            self.bl_mat["is_eu07_mat"] = "true"

            with open(filepath, encoding="latin-1") as matfile:
                eu07_mat = eu07_tools.mat.load(matfile)
                self.nodify_mat_mapping(eu07_mat)
        else:  # standalone texture
            self._import_texture(filepath, "texture_diffuse")

        return self.bl_mat

    def _import_texture(self, abspath, node_name, parent=None):
        if abspath:

            img_node = self.nodes.new("ShaderNodeTexImage")
            img_node.name = node_name
            img_node.label = node_name
            img_node.parent = parent

            if abspath.endswith(".dds"):
                img_node.texture_mapping.scale[1] = -1

            img_node.image = bpy.data.images.load(abspath, check_existing=True)

            if node_name == "texture_normalmap":
                img_node.image.colorspace_settings.name = 'Non-Color'
                normal_map_node = self.nodes.new("ShaderNodeNormalMap")
                normal_map_node.parent = parent

                self.links.new(img_node.outputs[0], normal_map_node.inputs[1])

                # NOTE: Normal maps look kinda bad so i disabled link to shader slot.
                if not parent and False:
                    self.links.new(normal_map_node.outputs[0],
                                   self.nodes.get("Principled BSDF").inputs[self.NORMAL_INPUT])

            elif node_name == "texture_diffuse" and not parent:
                self.links.new(img_node.outputs[0], self.bsdf.inputs["Base Color"])
                self.links.new(img_node.outputs[1], self.bsdf.inputs["Alpha"])

