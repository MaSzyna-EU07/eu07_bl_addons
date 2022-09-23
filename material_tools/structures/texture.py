import bpy

import eu07_tools

class EU07_Texture(bpy.types.PropertyGroup):
    @property
    def bl_node(self):
        return self.id_data

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


def register():
    bpy.utils.register_class(EU07_Texture)
    bpy.types.ShaderNodeTexImage.eu07_texture = bpy.props.PointerProperty(type=EU07_Texture)


def unregister():
    bpy.utils.unregister_class(EU07_Texture)
    del bpy.types.ShaderNodeTexImage.eu07_texture