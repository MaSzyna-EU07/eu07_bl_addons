import bpy

from ..common import create_material_from_path

def get_materials_for_trajectory(map_names, asset_searcher):
    materials = []

    for i, map_name in enumerate(map_names):
        materials.append(create_material_from_path(asset_searcher.textures.find(map_name)))

    return materials