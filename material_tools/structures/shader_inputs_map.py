import bpy


class EU07_ShaderInputAliasable(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty() # Name must match input name in node (Capitalized letters, no "texture_" prefix)
    unit_index: bpy.props.IntProperty(min=1) # Unit index


def register():
    bpy.utils.register_class(EU07_ShaderInputAliasable)
    bpy.types.NodeTree.eu07_shader_input_aliasable = bpy.props.PointerProperty(type=EU07_ShaderInputAliasable)


def unregister():
    bpy.utils.unregister_class(EU07_ShaderInputAliasable)
    del bpy.types.NodeTree.eu07_shader_input_aliasable