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

    def _get_bsdf_node(self):
        for node in self.nodes:
            is_eu07_bsdf = (
                node.bl_idname == 'ShaderNodeGroup' and
                node.node_tree and node.node_tree.name == presets.BSDF_NODE_NAME
            )

            is_blender_bsdf = (not is_eu07_bsdf and "Bsdf" in node.bl_idname)

            if is_eu07_bsdf or is_blender_bsdf:
                return node

    def _get_image_node(self):
        bsdf = self._get_bsdf_node()

        links = bsdf.inputs[BSDF_TEXTURE_INPUT].links
        if links:
            return links[0].from_node