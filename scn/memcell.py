import bpy

import eu07_tools

from scn.sectorizer import Sectorizer

def create_memcell_from_element(element):
    memcell_object = bpy.data.objects.new(element.name, None)
    memcell_object.scn_properties.type_ = "node:memcell"
    memcell_object.scn_properties.node_max_distance = element.max_distance
    memcell_object.scn_properties.node_min_distance = element.min_distance
    memcell_object.location = element.location.swizzled()
    memcell_object.scn_properties.memcell_value_text = element.values[0]
    memcell_object.scn_properties.memcell_value_first = element.values[1]
    memcell_object.scn_properties.memcell_value_second = element.values[2]
    memcell_object.scn_properties.memcell_track_name = element.track_name

    Sectorizer.auto_put(memcell_object)

    return memcell_object

def create_memcell_from_object(memcell_object):
    element = eu07_tools.scn.create_element("node:memcell", memcell_object.name)
    element.location = eu07_tools.utils.swizzle_coords(memcell_object.location)
    element.max_distance = memcell_object.scn_properties.node_max_distance
    element.min_distance = memcell_object.scn_properties.node_min_distance
    element.values = [
        memcell_object.scn_properties.memcell_value_text,
        memcell_object.scn_properties.memcell_value_first,
        memcell_object.scn_properties.memcell_value_second
    ]
    element.track_name = memcell_object.scn_properties.memcell_track_name

    return element