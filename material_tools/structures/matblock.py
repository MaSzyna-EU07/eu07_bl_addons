import bpy

import eu07_tools

from ..utils import  SHADER_NAME_PREFIX, is_random_textureset_node, is_eu07_shader_node


class EU07_MATBlock(bpy.types.PropertyGroup):
    """ PropertyGroup interface object for Shader Nodegroups """

    # HACK: self.id_data returns main node tree so i took this workaround from
    # https://blender.stackexchange.com/questions/214446/adding-properties-to-a-shader-node
    @property
    def bl_node(self):
        nodes = [n for n in self.id_data.nodes if n.type == 'GROUP']
        for n in nodes:
            n.eu07_matblock.name = n.name

        return self.id_data.nodes.get(self.name)

    @property
    def bl_node_tree(self):
        return self.id_data

    @property
    def _shader_inputs_data(self):
        return self.bl_node.node_tree.eu07_shader_inputs_data

    def poll(self):
        return is_eu07_shader_node(self.bl_node)

    def hide_slots(self):
        for inp in self.bl_node.inputs:
            inp.hide = True

    def get_by_key(self, key):
        if key == "shader":
            return self._get_shader_name()

        input_ = self._shader_inputs_data.get_input_by_key(key, self.bl_node.inputs)

        if key.startswith("texture"):
            return self._get_texture(input_)
        elif key.startswith("param"):
            return self._get_param(input_)
        elif key in eu07_tools.mat.VARIANT_KEYS:
            return self._get_variant(input_)
        else:
            return input_.default_value

    def set_by_key(self, key, value):
        if key == "shader":
            # Shader must be set first, otherwise the inputs can't be found.
            self._set_shader_by_name(value)
            return

        input_ = self._shader_inputs_data.get_input_by_key(key, self.bl_node.inputs)
        input_.hide = False

        if key.startswith("texture"):
            alpha_input = self._shader_inputs_data.get_alpha_input_by_key(key, self.bl_node.inputs)
            self._set_texture(input_, alpha_input, value)
        elif key.startswith("param"):
            self._set_param(input_, value)
        elif key in eu07_tools.mat.VARIANT_KEYS:
            self._set_variant(input_, value)
        else:
            input_.default_value = value

    def is_key_used(self, key):
        return self._shader_inputs_data.is_key_used(key, self.bl_node.inputs)

    def iter_used_keys(self):
        yield from self._shader_inputs_data.iter_used_keys(self.bl_node.inputs)

    def _get_texture(self, input_):
        node = input_.links[0].from_node
        if is_random_textureset_node(node):
            return node.eu07_randomtextureset
        else:
            return node.eu07_texture

    def _set_texture(self, input_, alpha_input, entity):
        self.bl_node_tree.links.new(
            entity.bl_node.outputs[0],
            input_
        )

        if entity.texture_type == "TEXTURE" and alpha_input is not None:
            self.bl_node_tree.links.new(
                entity.bl_node.outputs[1],
                alpha_input
            )

    def _get_param(self, input_):
        if input_.default_value != "":
            return [float(x) for x in input_.default_value.strip().split(" ")]

        return []

    def _set_param(self, input_, value):
        input_.default_value = " ".join(str(x) for x in value)

    def _get_variant(self, input_):
        if input_.links:
            return input_.links[0].from_node.eu07_matblock

    def _set_variant(self, input_, value):
        self.bl_node_tree.links.new(
            value.bl_node.outputs[0],
            input_
        )

    def _get_shader_name(self):
        return self.bl_node.node_tree.name.replace(SHADER_NAME_PREFIX, "")

    def _set_shader_by_name(self, name):
        try:
            self.bl_node.node_tree = bpy.data.node_groups[f"{SHADER_NAME_PREFIX}{name}"]
        except KeyError:
            raise KeyError(f"[EU07] Trying to set non-existing shader node group {name}")


classes = (
    EU07_MATBlock,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.ShaderNodeGroup.eu07_matblock = bpy.props.PointerProperty(type=EU07_MATBlock)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.ShaderNodeGroup.eu07_matblock
