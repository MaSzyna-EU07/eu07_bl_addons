import pathlib

import bpy

import eu07_tools


class EU07_Texture(bpy.types.PropertyGroup):
    placeholder_path: bpy.props.StringProperty(
        name="Placeholder Path"
    )

    disable_wrap_s: bpy.props.BoolProperty(
        name="Disable Horizontal Wrap",
        default=False,
    )

    disable_wrap_t: bpy.props.BoolProperty(
        name="Disable Vertical Wrap",
        default=False,
    )

    use_sharpen: bpy.props.BoolProperty(
        name="Sharpen",
        default=False,
    )

    @property
    def texture_type(self):
        return "TEXTURE"

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
        if self.bl_node.image:
            if self.bl_node.image.source == 'GENERATED':
                return self.bl_node.image.name

            return eu07_tools.utils.shorten_asset_path(
                str(pathlib.Path(self.abspath).with_suffix(""))
            )

        if self.placeholder_path:
            return self.placeholder_path

        return "none"

    @property
    def shortpath_with_traits(self):
        sp = self.shortpath

        traits = ":"
        traits += "s" if self.disable_wrap_s else ""
        traits += "t" if self.disable_wrap_t else ""
        traits += "#" if self.use_sharpen else ""

        if sp != "none" and traits != ":":
            return f"{sp}{traits}"

        return sp


def register():
    bpy.utils.register_class(EU07_Texture)
    bpy.types.ShaderNodeTexImage.eu07_texture = bpy.props.PointerProperty(type=EU07_Texture)


def unregister():
    bpy.utils.unregister_class(EU07_Texture)
    del bpy.types.ShaderNodeTexImage.eu07_texture