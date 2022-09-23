import bpy

RANDOM_TEXTURESET_NAME = "[EU07] Random Texture Set"
MAX_TEXTURESET_SIZE = 4

class EU07_RandomTextureSet(bpy.types.PropertyGroup):
    def append_texture(self, texture):
        pass

    def remove_texture(self, texture):
        pass


def create_template():
    ng = bpy.data.node_groups.get(RANDOM_TEXTURESET_NAME)

    if ng is None:
        ng_output = ng.nodes.new("NodeGroupOutput")
        ng_input = ng.nodes.new("NodeGroupInput")

        ng.outputs.new("NodeSocketColor", "Output Texture")
        for i in range(MAX_TEXTURESET_SIZE):
            ng.inputs.new("NodeSocketColor", f"Texture{i+1}")

    return ng


def register():
    bpy.utils.register_class(EU07_RandomTextureSet)
    bpy.types.ShaderNodeGroup.eu07_randomtextureset = bpy.props.PointerProperty(type=EU07_RandomTextureSet)


def unregister():
    bpy.utils.unregister_class(EU07_RandomTextureSet)
    del bpy.types.ShaderNodeGroup.eu07_randomtextureset