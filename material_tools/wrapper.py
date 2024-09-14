import bpy
import presets

MATERIALOUT_INPUT = 0

BSDF_TEXTURE_INPUT = 0
BSDF_ALPHA_INPUT = 1
BSDF_OUTPUT = 0

IMAGE_VECTOR_INPUT = 0
IMAGE_COLOR_OUTPUT = 0
IMAGE_ALPHA_OUTPUT = 1

TRAITS_VECTOR_INPUT = 0
TRAITS_VECTOR_OUTPUT = 0

UVMAP_VECTOR_OUTPUT = 0

TEXTURETRAITS_NODE_NAME = "[EU07] Texture Traits"


class MaterialWrapper:
    def __init__(self, material):
        self.material = material
        self.material.use_nodes = True
        self.nodes = material.node_tree.nodes
        self.links = material.node_tree.links

    # TODO: Deprecate
    def clean(self):
        for node in self.material.node_tree.nodes:
            if "Output" not in node.bl_idname:
                self.material.node_tree.nodes.remove(node)

    def initialize(self):
        self.nodes.clear()

        output = self.nodes.new("ShaderNodeOutputMaterial")
        output.location = (0, 0)

        bsdf = self.nodes.new("ShaderNodeGroup")
        bsdf.node_tree = bpy.data.node_groups.get(presets.BSDF_NODE_NAME)
        bsdf.location = (output.location.x - 300, 0)

        img_node = self.nodes.new("ShaderNodeTexImage")
        img_node.location = (bsdf.location.x - 300, 0)
        img_node.interpolation = 'Linear'

        traits_node = self.nodes.new("ShaderNodeGroup")
        traits_node.node_tree = bpy.data.node_groups.get(TEXTURETRAITS_NODE_NAME)
        traits_node.location = (img_node.location.x - 200, 0)

        uvmap_node = self.nodes.new("ShaderNodeUVMap")
        uvmap_node.location = (traits_node.location.x - 200, 0)

        self.links.new(
            uvmap_node.outputs[UVMAP_VECTOR_OUTPUT],
            traits_node.inputs[TRAITS_VECTOR_INPUT]
        )

        self.links.new(
            traits_node.outputs[TRAITS_VECTOR_OUTPUT],
            img_node.inputs[IMAGE_VECTOR_INPUT]
        )

        self.links.new(
            img_node.outputs[IMAGE_COLOR_OUTPUT],
            bsdf.inputs[BSDF_TEXTURE_INPUT]
        )

        self.links.new(
            img_node.outputs[IMAGE_ALPHA_OUTPUT],
            bsdf.inputs[BSDF_ALPHA_INPUT]
        )

        self.links.new(
            bsdf.outputs[BSDF_OUTPUT],
            output.inputs[MATERIALOUT_INPUT]
        )

        self.material.use_backface_culling = True
        self.material.use_transparency_overlap = False

    # TODO: Deprecate
    def set_diffuse_color(self, diffuse_color):
        bsdf = self._get_bsdf_node()
        bsdf.inputs[BSDF_TEXTURE_INPUT].default_value = [*diffuse_color, 1]

    # TODO: Deprecate
    def get_diffuse_color(self):
        bsdf = self._get_bsdf_node()
        return bsdf.inputs[BSDF_TEXTURE_INPUT].default_value

    def set_diffusemap(self, image):
        img_node = self._get_image_node()
        img_node.image = image

        if img_node.image.filepath.endswith(".dds"):
            img_node.texture_mapping.scale[1] = -1

    def get_diffusemap(self):
        img_node = self._get_image_node()

        if img_node:
            return img_node.image

    # TODO: Deprecate
    def set_opacity(self, opacity: float):
        return

    def _get_bsdf_node(self) -> bpy.types.ShaderNode:
        for node in self.nodes:
            if node.label == presets.BSDF_NODE_NAME:
                return node

    def _get_image_node(self):
        for node in self.nodes:
            if node.bl_idname == 'ShaderNodeTexImage':
                return node