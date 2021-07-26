from pathlib import Path

import bpy
import eu07_tools
from eu07_tools.utils import AssetSearcher


class EU07WeatherSettingsPanel(bpy.types.Panel):
    bl_idname = "SCENE_PT_eu07weather"
    bl_label = "Weather Settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "[EU07] Utility"

    def draw(self, context):
        scene = context.scene

        box = self.layout.box()
        box.label(text="here comes the sun, dun dun dun dun...")



def get_root(abspath=""):
    try:
        root = eu07_tools.utils.find_asset_root(abspath)
    except ValueError:
        root = bpy.context.preferences.addons['eu07_bl_addons'].preferences.root
        if not root:
            raise ValueError(f"Can't find root path for {abspath}")

    return root

def get_path_from_material(material):
    if material:
        if material.get("is_eu07_mat") and material["is_eu07_mat"] == "true":
            path = Path(material.name)
            if "textures" in path.parts:
                return str(path.relative_to("textures"))

        elif material.use_nodes:
            # Get the nodes in the node tree
            nodes = material.node_tree.nodes
            # Get a principled node
            principled = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
            # Get the slot for 'base color'
            base_color = principled.inputs['Base Color']  # Or principled.inputs[0]
            if base_color.links:
                link = base_color.links[0]
                link_node = link.from_node
                return eu07_tools.utils.shorten_asset_path(link_node.image.filepath)

    return "none"
