import pathlib

import bpy

# TODO: Move it away, too tight cohesion between modules

from material_tools.utils import BSDF_COLOR_INPUT, BSDF_SPECULAR_INPUT, BSDF_ROUGHNESS_INPUT, BSDF_ALPHA_INPUT, \
    is_eu07_shader_node, RANDOM_TEXTURESET_NAME


class EU07_Material(bpy.types.PropertyGroup):
    mat_source_path: bpy.props.StringProperty(
        name="MAT Source Path",
        subtype='FILE_PATH'
    )

    @property
    def is_mat(self):
        output = self._get_output_node()
        links = output.inputs[0].links
        if links:
            node = links[0].from_node
            return is_eu07_shader_node(node)

        return False

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
            if is_eu07_shader_node(node):
                output = node.outputs[0]

                is_nested = any([
                    is_eu07_shader_node(link.to_node)
                    for link in output.links
                ])
                if not is_nested:
                    return node.eu07_matblock

    @mat_root.setter
    def mat_root(self, new_root):
        output = self._get_output_node()

        self.bl_material.node_tree.links.new(
            new_root.bl_node.outputs[0],
            output.inputs[0],
        )

    def init(self):
        """ Initialize material """
        self.bl_material.use_nodes = True
        self.bl_material.use_backface_culling = True
        self.bl_material.show_transparent_back = False

    def create_texture(self):
        node = self.bl_material.node_tree.nodes.new('ShaderNodeTexImage')
        return node.eu07_texture

    def create_matblock(self):
        node = self.bl_material.node_tree.nodes.new('ShaderNodeGroup')
        node.inputs.new("NodeSocketShader", "Output")

        return node.eu07_matblock

    def create_randomtextureset(self):
        node = self.bl_material.node_tree.nodes.new('ShaderNodeGroup')
        node.node_tree = bpy.data.node_groups.get(RANDOM_TEXTURESET_NAME)
        return node.eu07_randomtextureset

    def set_single_texture(self, texture):
        bsdf = self._get_bsdf_node()

        self.bl_material.node_tree.links.new(
            texture.bl_node.outputs[0],
            bsdf.inputs[BSDF_COLOR_INPUT]
        )

        self.bl_material.node_tree.links.new(
            texture.bl_node.outputs[1],
            bsdf.inputs[BSDF_ALPHA_INPUT]
        )

    def get_opacity_for_submodel(self):
        if self.bl_material.blend_method == 'BLEND':
            return 0

        return 1

    @property
    def shortpath(self):
        if self.is_mat:
            return str(pathlib.Path(self.mat_source_path).with_suffix(""))
        else:
            bsdf = self._get_bsdf_node()
            image_node = self._get_diffuse_texture_node(bsdf)

            if image_node:
                return image_node.eu07_texture.shortpath

        return "none"

    def iter_image_textures(self):
        for node in self.bl_material.node_tree.nodes:
            if node.bl_idname == "ShaderNodeTexImage":
                if node.image:
                    yield node.image

    def clear(self):
        self.bl_material.node_tree.nodes.clear()

    def _get_diffuse_texture_node(self):
        bsdf = self._get_bsdf_node()

        if not bsdf:
            return None

        if bsdf.inputs[BSDF_COLOR_INPUT].links:
            link = bsdf.inputs[BSDF_COLOR_INPUT].links[0]
            node = link.from_node

            return node

    def _get_bsdf_node(self):
        for node in self.bl_material.node_tree.nodes:
            if "Bsdf" in node.bl_idname:
                return node

        bsdf = self.bl_material.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs[BSDF_SPECULAR_INPUT].default_value = 0
        bsdf.inputs[BSDF_ROUGHNESS_INPUT].default_value = 1

        return bsdf

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