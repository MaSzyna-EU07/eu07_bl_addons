import pathlib

import bpy

import eu07_tools
from . import matblock as matblock_mod
from . import randomtextureset as randomtextureset_mod

BSDF_COLOR_INPUT = 0
BSDF_SPECULAR_INPUT = 7
BSDF_ROUGHNESS_INPUT = 9
BSDF_ALPHA_INPUT = 21

class EU07_Material(bpy.types.PropertyGroup):
    is_mat: bpy.props.BoolProperty(
        name="Is MAT",
        default=False
    )

    mat_source_path: bpy.props.StringProperty(
        name="MAT Source Path",
        subtype='FILE_PATH'
    )

    @property
    def bl_material(self):
        # To ensure if node tree exists, a little hack here
        return self.id_data

    @property
    def name(self):
        return self.bl_material.name

    @name.setter
    def name(self, name):
        self.bl_material.name = name

    @property
    def mat_root(self):
        if not self.is_mat:
            return None

        for node in self.bl_material.node_tree.nodes:
            if node.type == 'GROUP' and node.eu07_matblock.is_valid:
                output = node.outputs[0]

                is_nested = any([
                    link.to_node.type == 'GROUP' and node.eu07_matblock.is_valid
                    for link in output.links
                ])
                if not is_nested:
                    return node.eu07_matblock

    def configure(self):
        self.bl_material.use_nodes = True
        bsdf = self._get_bsdf_node()

        bsdf.inputs[BSDF_SPECULAR_INPUT].default_value = 0
        bsdf.inputs[BSDF_ROUGHNESS_INPUT].default_value = 1
        self.bl_material.use_backface_culling = True
        self.bl_material.show_transparent_back = False

    def create_texture(self):
        node = self.bl_material.node_tree.nodes.new('ShaderNodeTexImage')
        return node.eu07_texture

    def create_matblock(self):
        node = self.bl_material.node_tree.nodes.new('ShaderNodeGroup')
        node.node_tree = matblock_mod.get_template()
        return node.eu07_matblock

    def create_randomtextureset(self):
        node = self.bl_material.node_tree.nodes.new('ShaderNodeGroup')
        node.node_tree = randomtextureset_mod.get_template()
        return node.eu07_randomtextureset

    def set_active_color_texture(self, texture):
        bsdf = self._get_bsdf_node()
        self.bl_material.node_tree.links.new(
            texture.bl_node.outputs[0],
            bsdf.inputs[BSDF_COLOR_INPUT]
        )
        self.bl_material.node_tree.links.new(
            texture.bl_node.outputs[1],
            bsdf.inputs[BSDF_ALPHA_INPUT]
        )

    def get_active_color_texture(self):
        bsdf = self._get_bsdf_node()

        links = bsdf.inputs[BSDF_COLOR_INPUT].links
        if links:
            node = links[0].from_node
            if node.bl_idname == "ShaderNodeTexImage":
                return node.image

    def get_opacity_for_submodel(self):
        if self.bl_material.blend_method == 'BLEND':
            return 0

        return 1

    @property
    def shortpath(self):
        if self.is_mat:
            return str(pathlib.Path(self.mat_source_path).with_suffix(".mat"))
        else:
            bsdf = self._get_bsdf_node()
            image_node = self._get_diffuse_texture_node(bsdf)

            if image_node:
                return eu07_tools.utils.shorten_asset_path(image_node.image.filepath)

        return "none"

    def iter_image_textures(self):
        for node in self.bl_material.node_tree.nodes:
            if node.bl_idname == "ShaderNodeTexImage":
                if node.image:
                    yield node.image

    def reset(self):
        self.bl_material.node_tree.nodes.clear()

        self.bl_material.node_tree.links.new(
            self._get_bsdf_node().outputs[0],
            self._get_output_node().inputs[0]
        )

    def _get_diffuse_texture_node(self, bsdf):
        if not bsdf:
            return None

        if bsdf.inputs[BSDF_COLOR_INPUT].links:
            link = bsdf.inputs.links[0]
            node = link.from_node

            return node

    def _get_bsdf_node(self):
        for node in self.bl_material.node_tree.nodes:
            if "Bsdf" in node.bl_idname:
                return node

        return self.bl_material.node_tree.nodes.new("ShaderNodeBsdfPrincipled")

    def _get_output_node(self):
        for node in self.bl_material.node_tree.nodes:
            if "OutputMaterial" in node.bl_idname:
                return node

        return self.bl_material.node_tree.nodes.new("ShaderNodeOutputMaterial")


def register():
    bpy.utils.register_class(EU07_Material)
    bpy.types.Material.eu07_material = bpy.props.PointerProperty(type=EU07_Material)


def unregister():
    bpy.utils.unregister_class(EU07_Material)
    del bpy.types.Material.eu07_material