import bpy

BSDF_COLOR_INPUT = 0
BSDF_SPECULAR_INPUT = 7
BSDF_ROUGHNESS_INPUT = 9
BSDF_ALPHA_INPUT = 21
BSDF_NORMAL_INPUT = 22

IMAGE_COLOR_OUTPUT = 0
IMAGE_ALPHA_OUTPUT = 1

NORMALMAP_COLOR_INPUT = 1
NORMALMAP_NORMAL_OUTPUT = 0


class MaterialWrapper:
    def __init__(self, material):
        self.material: bpy.types.Material = material
        self._node_tree: bpy.types.NodeTree = self.material.node_tree

    def initialize(self):
        self.material.use_nodes = True
        bsdf = self._get_bsdf_node()

        bsdf.inputs[BSDF_SPECULAR_INPUT].default_value = 0
        bsdf.inputs[BSDF_ROUGHNESS_INPUT].default_value = 1
        self.material.use_backface_culling = True

    def set_diffuse(self, image: bpy.types.Image):
        bsdf = self._get_bsdf_node()

        img_node = self._create_image_node(image)
        img_node.location = (-500, 300)

        link_color = self._node_tree.links.new(
            img_node.outputs[IMAGE_COLOR_OUTPUT],
            bsdf.inputs[BSDF_COLOR_INPUT]
        )
        link_alpha = self._node_tree.links.new(
            img_node.outputs[IMAGE_ALPHA_OUTPUT],
            bsdf.inputs[BSDF_ALPHA_INPUT]
        )

    def get_diffusemap(self):
        bsdf = self._get_bsdf_node()

        links = bsdf.inputs[BSDF_COLOR_INPUT].links
        if links:
            node = links[0].from_node
            if node.bl_idname == "ShaderNodeTexImage":
                return node.image

    def set_normalmap(self, image: bpy.types.Image):
        image.colorspace_settings.name = 'Non-Color'

        bsdf = self._get_bsdf_node()

        img_node = self._create_image_node(image)
        img_node.location = (-500, -300)

        normalmap_node = self._node_tree.nodes.new('ShaderNodeNormalMap')
        normalmap_node.location = (-250, -300)

        link1 = self._node_tree.links.new(
            img_node.outputs[IMAGE_COLOR_OUTPUT],
            normalmap_node.inputs[NORMALMAP_COLOR_INPUT]
        )

        link2 = self._node_tree.links.new(
            normalmap_node.outputs[NORMALMAP_NORMAL_OUTPUT],
            bsdf.inputs[BSDF_NORMAL_INPUT]
        )

    def set_opacity(self, opacity: float):
        if opacity == 1:
            self.material.blend_method = 'OPAQUE'
        else:
            self.material.blend_method = 'BLEND'

    def get_opacity(self) -> float:
        if self.material.blend_method == 'OPAQUE':
            return 1
        elif self.material.blend_method == 'BLEND':
            return 0

        return 1

    def _create_image_node(self, image: bpy.types.Image) -> bpy.types.ShaderNodeTexImage:
        img_node = self._node_tree.nodes.new('ShaderNodeTexImage')

        img_node.image = image
        img_node.interpolation = 'Linear'

        if img_node.image.filepath.endswith(".dds"):
            img_node.texture_mapping.scale[1] = -1

        return img_node

    def _get_bsdf_node(self) -> bpy.types.ShaderNode:
        for node in self._node_tree.nodes:
            if "Bsdf" in node.bl_idname:
                return node
