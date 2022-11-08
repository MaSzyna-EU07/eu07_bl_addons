import bpy
import eu07_tools
from common import uilist_safe_index_after_delete

from ..nodegroups.randomtextureset import RANDOM_TEXTURESET_NAME
from ..utils import get_active_material, get_active_material_node


class EU07_MATBlock(bpy.types.PropertyGroup):

    size: bpy.props.FloatVectorProperty(
        name="Size",
        size=2,
        default=(-1, -1),
        min=-1,
    )


    # HACK: self.id_data returns main node tree so i took this workaround from
    # https://blender.stackexchange.com/questions/214446/adding-properties-to-a-shader-node
    @property
    def bl_node(self):
        nodes = [n for n in self.id_data.nodes if n.type == 'GROUP']
        for n in nodes:
            n.eu07_matblock.name = n.name

        return self.id_data.nodes.get(self.name)

    @property
    def bl_node_tree(self):
        return self.id_data

    @property
    def is_valid(self):
        return self.bl_node.node_tree.name.startswith("[EU07] Shader:")

    def set_to_texture_slot(self, entity, slot_name):
        self.bl_node_tree.links.new(
            entity.bl_node.outputs[0],
            self._get_texture_slot_input(slot_name)
        )

    def get_from_texture_slot(self, slot_name):
        input_ = self._get_texture_slot_input(slot_name)
        if input_.links:
            node = input_.links[0].from_node
            if node.bl_idname == "ShaderNodeGroup" and node.node_tree.name == RANDOM_TEXTURESET_NAME:
                return node.eu07_randomtextureset
            else:
                return node.eu07_texture

    def set_subblock(self, subblock, variant_name):
        self.bl_node_tree.links.new(
            subblock.bl_node.outputs[0],
            self._get_variant_input(variant_name)
        )

    def get_subblock(self, variant_name):
        input_ = self._get_variant_input(variant_name)
        if input_.links:
            return input_.links[0].from_node.eu07_matblock

    def _get_texture_slot_input(self, slot_name):
        for input in self.bl_node.inputs:
            if input.name.lower() == slot_name.lower():
                return input

    def _get_variant_input(self, variant_name):
        for input_ in self.bl_node.inputs:
            if input_.name.lower() == variant_name.lower():
                return input_


def poll_helper(context):
    active_mat = get_active_material(context)
    active_node = get_active_material_node(active_mat)
    return active_node.bl_idname == "ShaderNodeGroup" and active_node.node_tree.name.startswith("[EU07] Shader:")

classes = (
    EU07_MATBlock,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.ShaderNodeGroup.eu07_matblock = bpy.props.PointerProperty(type=EU07_MATBlock)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.ShaderNodeGroup.eu07_matblock