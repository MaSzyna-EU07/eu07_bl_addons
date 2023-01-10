import pathlib

import bpy

import eu07_tools
from material_tools.nodegroups import texture_wrap_traits
from material_tools.utils import WRAP_TRAITS_NAME


class EU07_Texture(bpy.types.PropertyGroup):
    placeholder_path: bpy.props.StringProperty(
        name="Placeholder Path"
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

    @property
    def bl_node_tree(self):
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

        traits_node = self._get_traits_node()



        traits = ":"

        # NOTE: vanilla blender clipping allows to clip in both axes, so we can use it as a convienient option
        if self.bl_node.extension == 'EXTEND':
            traits += "st"

        # but if there's no vanilla clipping, we can use our custom solution
        else:
            traits += "s" if self.disable_wrap_s else ""
            traits += "t" if self.disable_wrap_t else ""

        traits += "#" if self.use_sharpen else ""

        if sp != "none" and traits != ":":
            return f"{sp}{traits}"

        return sp

    @property
    def disable_wrap_s(self):
        traits_node = self._get_traits_node()
        if not traits_node:
            return False
        return traits_node.inputs[1].default_value == 1

    @disable_wrap_s.setter
    def disable_wrap_s(self, disable_wrap_s):
        traits_node = self._get_traits_node(create_missing=True)
        traits_node.inputs[1].default_value = int(disable_wrap_s)

    @property
    def disable_wrap_t(self):
        traits_node = self._get_traits_node()
        if not traits_node:
            return False
        return traits_node.inputs[2].default_value == 1

    @disable_wrap_t.setter
    def disable_wrap_t(self, disable_wrap_t):
        traits_node = self._get_traits_node(create_missing=True)
        traits_node.inputs[2].default_value = int(disable_wrap_t)


    def _get_traits_node(self, create_missing=False):
        links = self.bl_node.inputs[0].links
        if links:
            node = links[0].from_node
            if node.bl_idname == "ShaderNodeGroup" and node.node_tree.name == WRAP_TRAITS_NAME:
                return node
        else:
            if create_missing:
                traits_node = self.bl_node_tree.nodes.new('ShaderNodeGroup')
                traits_node.node_tree = texture_wrap_traits.generate()

                uvnode = self.bl_node_tree.nodes.new("ShaderNodeUVMap")

                self.bl_node_tree.links.new(
                    traits_node.outputs[0],
                    self.bl_node.inputs[0]
                )

                self.bl_node_tree.links.new(
                    uvnode.outputs[0],
                    traits_node.inputs[0]
                )

                return traits_node

def register():
    bpy.utils.register_class(EU07_Texture)
    bpy.types.ShaderNodeTexImage.eu07_texture = bpy.props.PointerProperty(type=EU07_Texture)


def unregister():
    bpy.utils.unregister_class(EU07_Texture)
    del bpy.types.ShaderNodeTexImage.eu07_texture