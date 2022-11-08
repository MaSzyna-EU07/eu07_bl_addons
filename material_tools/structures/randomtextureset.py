import bpy


class EU07_RandomTextureSet(bpy.types.PropertyGroup):
    # HACK: self.id_data returns main node tree so i took this workaround from
    # https://blender.stackexchange.com/questions/214446/adding-properties-to-a-shader-node
    @property
    def texture_type(self):
        return "RANDOM_TEXTURESET"

    @property
    def bl_node(self):
        nodes = (n for n in self.id_data.nodes if n.type == 'GROUP')
        for n in nodes:
            n.eu07_randomtextureset.name = n.name

        return self.id_data.nodes.get(self.name)

    def append_texture(self, texture):
        for input_ in self.bl_node.inputs:
            if not input_.links:
                self.bl_node.id_data.links.new(
                    texture.bl_node.outputs[0],
                    input_
                )
                return

    def iter_textures(self):
        for input_ in self.bl_node.inputs:
            if input_.links:
                yield input_.links[0].from_node.eu07_texture

    @property
    def mat_alias(self):
        return self.bl_node.label

    @mat_alias.setter
    def mat_alias(self, alias):
        self.bl_node.label = alias


def register():
    bpy.utils.register_class(EU07_RandomTextureSet)
    bpy.types.ShaderNodeGroup.eu07_randomtextureset = bpy.props.PointerProperty(type=EU07_RandomTextureSet)


def unregister():
    bpy.utils.unregister_class(EU07_RandomTextureSet)
    del bpy.types.ShaderNodeGroup.eu07_randomtextureset