import pathlib

import bpy

import eu07_tools
from eu07_tools.mat.shaderparser import ShaderParser

from ..utils import (
    BSDF_COLOR_INPUT,
    BSDF_ROUGHNESS_INPUT,
    BSDF_ALPHA_INPUT,
    BSDF_SPECULAR_INPUT,
    BSDF_METALLIC_INPUT,
    BSDF_NORMAL_INPUT,
)



COLOR_TEXTURE_ALIASES = ("albedo", "diffuse", "color", "base_color", "basecolor")
PARAMS_SOCKET_TYPES = {
    1: "NodeSocketFloat",
    2: "NodeSocketVector",
    3: "NodeSocketVector",
    4: "NodeSocketColor",
}

# NOTE: This is ugly and could be done better, but it works, so low priority for that
class ShaderNodeGroupGenerator:
    def __init__(self, asset_searcher):
        self.asset_searcher = asset_searcher

        # stuff for tree building, to avoid long parameters list
        self._ng = None
        self._ng_input = None
        self._ng_output = None
        self._bsdf = None
        self._input_index = 0

        # map key: setup callback, default param_list, has alpha
        self._map_setups = {
            "diffuse": [
                self._diffuse_setup,
                (1, 1, 1, 1),
            ],
            "normalmap": [
                self._normalmap_setup,
                (0.5, 0.5, 1, 1),
            ],
            "albedo": [
                self._albedo_setup,
                (1, 1, 1, 1),
            ],
            "params": [
                self._params_setup,
                (0, 0, 1, 1),
            ]
        }

    def generate_from_filename(self, filename):
        """ Builds node group based on data read from given file key """
        self.asset_searcher.shaders.remove_extension(".vert")
        abspath = self.asset_searcher.shaders.find(filename)
        self.asset_searcher.shaders.add_extension(".vert")

        if abspath:
            parser = ShaderParser(self.asset_searcher)
            shader_data = parser.parse_from_abspath(abspath)

            name = "[EU07] Shader: " + str(pathlib.Path(filename.replace("mat_", "")).with_suffix(""))
            return self.generate_from_data(shader_data, name)

    def generate_from_data(self, shader_data, name):
        """
        Builds node group with inputs based on passed shader data and given key.
        If group with given key already exists, it's content is rebuilded.
        """
        self._ng = bpy.data.node_groups.get(name)
        if self._ng:
            return self._ng

        self._ng = bpy.data.node_groups.new(name, "ShaderNodeTree")

        # Add basic nodes
        self._ng_input = self._ng.nodes.new("NodeGroupInput")
        self._ng_output = self._ng.nodes.new("NodeGroupOutput")
        self._bsdf = self._ng.nodes.new("ShaderNodeBsdfPrincipled")

        self._bsdf.inputs[BSDF_SPECULAR_INPUT].default_value = 0
        self._bsdf.inputs[BSDF_ROUGHNESS_INPUT].default_value = 1

        self._ng.outputs.new("NodeSocketShader", "Output")

        self._ng.links.new(
            self._bsdf.outputs[0],
            self._ng_output.inputs[0],
        )

        self._input_index = 0
        for texture_data_object in shader_data.textures:
            slotname = texture_data_object.name.replace("_", " ").title()
            inp = self._ng.inputs.new("NodeSocketColor", slotname)

            has_alpha = texture_data_object.components in ("RGBA", "sRGB_A")

            key_default, key_alias = self._get_default_and_alias_keys(texture_data_object, "texture")
            self._ng.eu07_shader_inputs_data.register_input(
                self._input_index,
                key_default, key_alias,
                has_alpha=has_alpha
            )

            setup_data = self._map_setups.get(texture_data_object.name)
            if setup_data:
                setup_func, default_value = setup_data

            if setup_data:
                setup_func()
                inp.default_value = default_value

                if has_alpha:
                    inp = self._ng.inputs.new("NodeSocketFloat", f"{texture_data_object.name.capitalize()} Alpha")
                    inp.default_value = 1
                    inp.max_value = 1
                    inp.min_value = 1
                    self._input_index += 1

                    # Only color texture's alpha should be connected to alpha slot in BSDF
                    if texture_data_object.name in COLOR_TEXTURE_ALIASES:
                        self._alpha_setup()

            self._input_index += 1

        for param_data_object in shader_data.params:
            slotname = param_data_object.name.replace("_", " ").title()

            socket_type = PARAMS_SOCKET_TYPES.get(param_data_object.size)

            self._ng.inputs.new(socket_type, slotname)

            key_default, key_alias = self._get_default_and_alias_keys(param_data_object, "param")
            self._ng.eu07_shader_inputs_data.register_input(
                self._input_index,
                key_default, key_alias,
                param_size=param_data_object.size
            )

            self._input_index += 1

        opacity_inp = self._ng.inputs.new("NodeSocketFloat", "Opacity")
        opacity_inp.default_value = 1
        opacity_inp.min_value = 0
        opacity_inp.max_value = 1
        self._ng.eu07_shader_inputs_data.register_input(self._input_index, "opacity")
        self._input_index += 1

        selfillum_inp = self._ng.inputs.new("NodeSocketFloat", "SelfIllum")
        selfillum_inp.default_value = -1
        selfillum_inp.min_value = -1
        selfillum_inp.max_value = 2
        self._ng.eu07_shader_inputs_data.register_input(self._input_index, "selfillum")
        self._input_index += 1

        shadowrank_inp = self._ng.inputs.new("NodeSocketInt", "Shadow Rank")
        shadowrank_inp.default_value = 3
        shadowrank_inp.min_value = 1
        shadowrank_inp.max_value = 3
        self._ng.eu07_shader_inputs_data.register_input(self._input_index, "shadow_rank")
        self._input_index += 1

        size_inp = self._ng.inputs.new("NodeSocketVectorTranslation", "Size")
        size_inp.default_value = [-1, -1, 0]
        self._ng.eu07_shader_inputs_data.register_input(self._input_index, "size")
        self._input_index += 1

        for variant_name in eu07_tools.mat.VARIANT_KEYS:
            self._ng.inputs.new("NodeSocketShader", variant_name.capitalize())

            self._ng.eu07_shader_inputs_data.register_input(self._input_index, variant_name)

            self._input_index += 1

        return self._ng

    def _get_default_and_alias_keys(self, data_object, keyword):
        key_default = f"{keyword}{data_object.unit_index}"
        key_alias = f"{keyword}_{data_object.name}"
        return key_default, key_alias


    def _diffuse_setup(self):
        self._ng.links.new(
            self._ng_input.outputs[self._input_index],
            self._bsdf.inputs[BSDF_COLOR_INPUT]
        )

    def _alpha_setup(self):
        self._ng.links.new(
            self._ng_input.outputs[self._input_index],
            self._bsdf.inputs[BSDF_ALPHA_INPUT]
        )

    def _normalmap_setup(self):
        sep = self._ng.nodes.new("ShaderNodeSeparateColor")
        comb = self._ng.nodes.new("ShaderNodeCombineColor")
        nrm = self._ng.nodes.new("ShaderNodeNormalMap")

        # input color to Separate
        self._ng.links.new(
            self._ng_input.outputs[self._input_index],
            sep.inputs[0]
        )

        # R to R
        self._ng.links.new(
            sep.outputs[0],
            comb.inputs[0]
        )

        # G to G
        self._ng.links.new(
            sep.outputs[1],
            comb.inputs[1]
        )

        # B = 1
        comb.inputs[2].default_value = 1

        # Combined to Normal Map
        self._ng.links.new(
            comb.outputs[0],
            nrm.inputs[1]
        )

        # Normal Map to output
        self._ng.links.new(
            nrm.outputs[0],
            self._bsdf.inputs[BSDF_NORMAL_INPUT]
        )

    def _albedo_setup(self):
        mix_rgb = self._get_albedo_mixrgb()

        self._ng.links.new(
            self._ng_input.outputs[self._input_index],
            mix_rgb.inputs[1]
        )

    def _params_setup(self):
        sep_rgb = self._ng.nodes.new("ShaderNodeSeparateColor")
        invert = self._ng.nodes.new("ShaderNodeInvert")
        mix_rgb = self._get_albedo_mixrgb()

        # link params map to color separator
        self._ng.links.new(
            self._ng_input.outputs[self._input_index],
            sep_rgb.inputs[0]
        )
        # link separated R to bsdf's metallic
        self._ng.links.new(
            sep_rgb.outputs[0],
            self._bsdf.inputs[BSDF_METALLIC_INPUT]
        )
        # link separated G to invert
        self._ng.links.new(
            sep_rgb.outputs[1],
            invert.inputs[0]
        )
        # link inverted G to bsdf's roughness
        self._ng.links.new(
            invert.outputs[0],
            self._bsdf.inputs[BSDF_ROUGHNESS_INPUT]
        )

        if mix_rgb:
            self._ng.links.new(
                sep_rgb.outputs[2],
                mix_rgb.inputs[2]
            )

    def _get_albedo_mixrgb(self):
        color_input = self._bsdf.inputs[BSDF_COLOR_INPUT]

        if color_input.links:
            candidate = color_input.links[0].from_node
            if candidate.bl_idname == "ShaderNodeMixRGB":
                return candidate

        mix_rgb = self._ng.nodes.new("ShaderNodeMixRGB")
        mix_rgb.inputs[0].default_value = 1

        self._ng.links.new(
            mix_rgb.outputs[0],
            self._bsdf.inputs[BSDF_COLOR_INPUT]
        )

        return mix_rgb


