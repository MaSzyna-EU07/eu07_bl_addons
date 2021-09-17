import bpy

import eu07_tools
from scn.sectorizer import Sectorizer
from common import get_root


def create_sound_from_element(element):
    speaker = bpy.data.speakers.new(element.name)
    sound_object = bpy.data.objects.new(element.name, speaker)
    sound_object.location = element.location.swizzled()

    asset_searcher = eu07_tools.utils.AssetSearcher(get_root())

    sound_object.scn_properties.node_max_distance = element.max_distance
    sound_object.scn_properties.node_min_distance = element.min_distance
    sound_object.scn_properties.type_ = "node:sound"
    sound_object.scn_properties.sound_path = asset_searcher.sounds.find(element.path)

    Sectorizer.auto_put(sound_object)


def create_element_from_sound(sound_object):
    element = eu07_tools.scn.create_element("node:sound", sound_object.name)

    element.max_distance = sound_object.scn_properties.node_max_distance
    element.min_distance = sound_object.scn_properties.node_min_distance
    element.location = eu07_tools.utils.swizzle_coords(sound_object.location)
    element.path = eu07_tools.utils.shorten_asset_path(sound_object.scn_properties.sound_path)

    return element