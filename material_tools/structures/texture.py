import bpy

import eu07_tools

class EU07_Texture(bpy.types.PropertyGroup):
    # HACK: self.id_data returns main node tree so i took this workaround from
    # https://blender.stackexchange.com/questions/214446/adding-properties-to-a-shader-node
    @property
    def bl_node(self):
        nodes = [n for n in self.id_data.nodes if n.type == 'TEX_IMAGE']
        for n in nodes:
            n.eu07_texture.name = n.name

        return self.id_data.nodes.get(self.name)

    def set_image_from_abspath(self, abspath):
        image = bpy.data.images.load(abspath, check_existing=True)
        self.bl_node.image = image

    @property
    def abspath(self):
        if self.bl_node.image:
            return self.bl_node.image.filepath

    @property
    def shortpath(self):
        if self.abspath:
            return eu07_tools.utils.shorten_asset_path(self.abspath)

        return "none"

    @property
    def mat_alias(self):
        return self.bl_node.label

    @mat_alias.setter
    def mat_alias(self, alias):
        self.bl_node.label = alias


def register():
    bpy.utils.register_class(EU07_Texture)
    bpy.types.ShaderNodeTexImage.eu07_texture = bpy.props.PointerProperty(type=EU07_Texture)


def unregister():
    bpy.utils.unregister_class(EU07_Texture)
    del bpy.types.ShaderNodeTexImage.eu07_texture