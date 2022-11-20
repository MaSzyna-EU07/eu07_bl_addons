import bpy


class EU07_ShaderInputsMapItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()  # Name must match input name in node (Titled Letters, no "texture_"/"param_" prefix)
    unit_index: bpy.props.IntProperty(min=1)  # Unit index


class EU07_ShaderInputsMap(bpy.types.PropertyGroup):
    """ Stores data about unit indices bound to texture aliases """
    items_textures: bpy.props.CollectionProperty(type=EU07_ShaderInputsMapItem)
    items_params: bpy.props.CollectionProperty(type=EU07_ShaderInputsMapItem)

    def add_texture_data(self, unit_index, name):
        item = self.items_textures.add()
        item.name = name
        item.unit_index = unit_index

    def add_param_data(self, unit_index, name):
        item = self.items_params.add()
        item.name = name
        item.unit_index = unit_index

    def get_texture_input_name(self, unit_index):
        for item in self.items_textures:
            if item.unit_index == unit_index:
                return item.name

    def get_texture_unit_index(self, input_name):
        for item in self.items_textures:
            if item.name == input_name:
                return item.unit_index

    def get_param_input_name(self, unit_index):
        for item in self.items_params:
            if item.unit_index == unit_index:
                return item.name

    def get_param_unit_index(self, input_name):
        for item in self.items_params:
            if item.name == input_name:
                return item.unit_index


classes = (
    EU07_ShaderInputsMapItem,
    EU07_ShaderInputsMap
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.NodeTree.eu07_shader_inputs_map = bpy.props.PointerProperty(type=EU07_ShaderInputsMap)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.NodeTree.eu07_shader_inputs_map