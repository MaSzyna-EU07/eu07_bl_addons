import bpy

import eu07_tools


class EU07_ShaderInputsDataItem(bpy.types.PropertyGroup):
    """ Stores data associated with EU07 Shader node inputs. Maps keys from MAT format to EU07 Shader node inputs. """

    input_index: bpy.props.IntProperty(
        name="Node Input Index",
        description="Node input index",
        default=0
    )
    key_default: bpy.props.StringProperty(
        name="Default Key",
        description="Default key (as in MAT format)",
        default=""
    )
    key_alias: bpy.props.StringProperty(
        name="Alias Key",
        description="Key (as in MAT format), contains default key's alias (if exists), empty string otherwise",
        default="",
    )
    has_alpha: bpy.props.BoolProperty(
        name="Has Alpha",
        description="True if this input has additional alpha input, false otherwise",
        default=False
    )
    param_size: bpy.props.IntProperty(
        name="Param Size",
        description="Size of the shader param vector. Used for providing correct export. 0 if input is not a param.",
        default=0
    )


class EU07_ShaderInputsData(bpy.types.PropertyGroup):
    items: bpy.props.CollectionProperty(type=EU07_ShaderInputsDataItem)

    def register_input(self, input_index, key_default, key_alias="", has_alpha=False, param_size=0):
        item = self.items.add()
        item.input_index = input_index
        item.key_default = key_default
        item.key_alias = key_alias
        item.has_alpha = has_alpha
        item.param_size = param_size

    def get_input_by_key(self, key, inputs):
        index = self._get_index_by_key(key)
        return inputs[index]

    def get_param_value_by_key(self, key, inputs):
        item = self._get_item_by_key(key)
        input_ = self.get_input_by_key(key, inputs)

        if item.param_size == 0:
            return []
        elif item.param_size == 2:
            return input_.default_value[:2]
        elif item.param_size == 1:
            return [input_.default_value]
        else:
            return input_.default_value

    def get_key_by_input(self, input, inputs):
        index = inputs.find(input.name)

        for item in self.items:
            if item.input_index == index:
                if item.key_alias:
                    return item.key_alias
                else:
                    return item.key_default

        return None

    def is_key_used(self, key, inputs):
        input_ = self.get_input_by_key(key, inputs)

        if input_.hide:
            return False

        if key.startswith("texture") or key in eu07_tools.mat.VARIANT_KEYS:
            if not input_.links:
                return False

        return True

    def iter_used_keys(self, inputs):
        # TODO: Check if this don't kill performance
        yield "shader"

        for input_ in inputs:
            key = self.get_key_by_input(input_, inputs)
            if key is not None and self.is_key_used(key, inputs):
                yield key

    def get_alpha_input_by_key(self, key, inputs):
        try:
            item = self._get_item_by_key(key)
        except KeyError:
            return None
        else:
            if item.has_alpha:
                return inputs[item.input_index + 1]

    def _get_index_by_key(self, key):
        try:
            item = self._get_item_by_key(key)
        except KeyError:
            return None
        else:
            return item.input_index

    def _get_item_by_key(self, key):
        for item in self.items:
            if (item.key_default == key or (item.key_alias and item.key_alias == key)):
                return item

        raise KeyError(f"Can't get EU07 Shader node input data for key {key}")

classes = (
    EU07_ShaderInputsDataItem,
    EU07_ShaderInputsData
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.NodeTree.eu07_shader_inputs_data = bpy.props.PointerProperty(type=EU07_ShaderInputsData)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.NodeTree.eu07_shader_inputs_data