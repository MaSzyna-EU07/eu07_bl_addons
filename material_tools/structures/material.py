import bpy

from . import matblock as matblock_mod
from . import randomtextureset as randomtextureset_mod

BSDF_COLOR_INPUT = 0
BSDF_ALPHA_INPUT = 21

class EU07_Material(bpy.types.PropertyGroup):
    is_mat: bpy.types.BoolProperty(
        name="Is MAT",
        default=False
    )

    mat_source_path: bpy.types.StringProperty(
        name="MAT Source Path",
        subtype='FILE_PATH'
    )

    @property
    def bl_material(self):
        return self.id_data

    @property
    def mat_root(self):
        if self.type != 'MAT':
            return None

        for node in self.bl_material.node_tree.nodes:
            if node.label == matblock_mod.NODEGROUP_NAME:
                output = node.outputs[0]

                is_nested = any([link.to_node.label == matblock_mod.NODEGROUP_NAME for link in output.links])
                if not is_nested:
                    return node.eu07_matblock

    def create_texture(self):
        node = self.bl_material.node_tree.nodes.new('ShaderNodeTexImage')
        return node.eu07_texture

    def create_matblock(self):
        node = self.bl_material.node_tree.nodes.new('ShaderNodeGroup')
        node.node_tree = matblock_mod.get_template()
        return node.eu07_matblock

    def create_randomtextureset(self):
        node = self.bl_material.node_tree.nodes.new('ShaderNodeGroup')
        node.node_tree = randomtextureset_mod.get_template()
        return node.eu07_randomtextureset

    def set_active_color_texture(self, texture):
        bsdf = self._get_bsdf_node()
        self.bl_material.node_tree.links.new(
            texture.bl_node.outputs[0],
            bsdf.inputs[BSDF_COLOR_INPUT]
        )
        self.bl_material.node_tree.links.new(
            texture.bl_node.outputs[1],
            bsdf.inputs[BSDF_ALPHA_INPUT]
        )


    @property
    def path_from_diffuse(self):
        if self.type != "TEXTURE":
            return ""

        bsdf = self._get_bsdf_node()
        image_node = self._get_diffuse_texture_node(bsdf)

        if image_node.image:
            return "dupa"

        return ""

    def _get_diffuse_texture_node(self, bsdf):
        if bsdf.inputs[BSDF_COLOR_INPUT].links:
            link = bsdf.inputs.links[0]
            node = link.from_node

            return node

    def _get_bsdf_node(self):
        for node in self.bl_material.node_tree.nodes:
            if "Bsdf" in node.bl_idname:
                return node


def register():
    bpy.utils.register_class(EU07_Material)
    bpy.types.Material.eu07_material = bpy.props.PointerProperty(type=EU07_Material)


def unregister():
    bpy.utils.unregister_class(EU07_Material)
    del bpy.types.Material.eu07_material