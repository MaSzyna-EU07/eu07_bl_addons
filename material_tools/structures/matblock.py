import bpy

from ..nodegroups.randomtextureset import RANDOM_TEXTURESET_NAME
from ..utils import get_active_material, get_active_material_node, SHADER_NAME_PREFIX


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
    def is_valid(self):
        """ Check if node group can be wrapped """
        return self.bl_node.node_tree.name.startswith(SHADER_NAME_PREFIX)

    def hide_slots(self):
        for inp in self.bl_node.inputs:
            inp.hide = True

    @property
    def shader(self):
        return self.bl_node.node_tree.name.replace(SHADER_NAME_PREFIX, "")

    @shader.setter
    def shader(self, name):
        try:
            self.bl_node.node_tree = bpy.data.node_groups[f"{SHADER_NAME_PREFIX}{name}"]
        except KeyError:
            raise KeyError(f"[EU07] Trying to set non-existing shader node group {name}")

    @property
    def opacity(self):
        return self._get_value("Opacity")

    @opacity.setter
    def opacity(self, opacity):
        self._set_value("Opacity", opacity)

    @property
    def selfillum(self):
        return self._get_value("SelfIllum")

    @selfillum.setter
    def selfillum(self, selfillum):
        self._set_value("SelfIllum", selfillum)

    @property
    def size(self):
        return [self._get_value("Size X"), self._get_value("Size Y")]

    @size.setter
    def size(self, size):
        self._set_value("Size X", size[0])
        self._set_value("Size Y", size[1])

    @property
    def shadow_rank(self):
        return self._get_value("Shadow Rank")

    @shadow_rank.setter
    def shadow_rank(self, shadow_rank):
        self._set_value("Shadow Rank", shadow_rank)

    def set_texture(self, key, entity):
        """ Set texture interface object for given key """
        input_ = self._get_input(key)
        input_.hide = False

        if input_ is not None:
            self.bl_node_tree.links.new(
                entity.bl_node.outputs[0],
                input_
            )

            # NOTE: Temporary workaround
            if "albedo" in key.lower() or "diffuse" in key.lower():
                self.bl_node_tree.links.new(
                    entity.bl_node.outputs[1],
                    self._get_input_by_name_part("Alpha")
                )

    def get_texture(self, key):
        """ Get texture interface object for given key """
        input_ = self._get_input(key)

        if input_ is not None and input_.links:
            node = input_.links[0].from_node
            if node.bl_idname == "ShaderNodeGroup" and node.node_tree.name == RANDOM_TEXTURESET_NAME:
                return node.eu07_randomtextureset
            else:
                return node.eu07_texture

    def set_param(self, key, value):
        """ Set shader param value to input with given name """
        input_ = self._get_input(key)
        input_.hide = False

        if input_ is not None:
            input_.default_value = " ".join(str(x) for x in value)
        else:
            raise KeyError(f"No key '{key}' in shader f'{self.shader}'")

    def get_param(self, key):
        """ Get shader param value from input with given name """
        input_ = self._get_input(key)

        return input_.default_value.strip()

    def set_variant(self, key, subblock):
        """ Set material variant to input with given name """
        input_ = self._get_input(key)
        input_.hide = False

        self.bl_node_tree.links.new(
            subblock.bl_node.outputs[0],
            input_
        )

    def get_variant(self, key):
        input_ = self._get_input(key)
        if input_.links:
            return input_.links[0].from_node.eu07_matblock

    def _set_value(self, key, value):
        """ Set value at given key """
        input_ = self._get_input(key)
        input_.hide = False

        input_.default_value = value

    def _get_value(self, key):
        """ Get value for given key """
        input_ = self._get_input(key)
        return input_.default_value

    def _get_input(self, key):
        for input_ in self.bl_node.inputs:
            if input_.name.lower() == key.lower():
                return input_

    def _get_input_by_name_part(self, part):
        for input_ in self.bl_node.inputs:
            if part.lower() in input_.name.lower():
                return input_


def poll_helper(context):
    active_mat = get_active_material(context)
    active_node = get_active_material_node(active_mat)
    return active_node.bl_idname == "ShaderNodeGroup" and active_node.node_tree.name.startswith(SHADER_NAME_PREFIX)


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