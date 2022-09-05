import math
import pathlib

import bpy
import eu07_tools
from scn.core import factory


class SceneryImporter:
    def __init__(self):
        pass

    def import_from_filepath(self, filepath):
        pass

    def import_from_file(self, file):
        pass

#TODO: Material lookup
#TODO: Prevent mesh_data from regeneration after each property update
    def _import_track(self, track_element):
        track_entity = factory.create_entity(track_element.type, track_element.name)
        track_entity.width = track_element.width
        track_entity.friction = track_element.friction
        track_entity.sound_distance = track_element.sound_distance
        track_entity.quality_flag = track_element.quality_flag
        track_entity.damage_flag = track_element.damage_flag
        track_entity.environment = track_element.environment
        track_entity.visibility = "vis" if track_element.is_visible else "unvis"
        track_entity.map1 = None
        track_entity.map1_length = track_element.mapping_length
        track_entity.map2 = None
        track_entity.geometry_params = track_element.geometry_params

        track_entity.p1 = track_element.p1
        track_entity.p1_roll = track_element.p1_roll

        track_entity.cv1 = track_element.cv1
        track_entity.cv2 = track_element.cv2

        track_entity.p2 = track_element.p2
        track_entity.p2_roll = track_element.p2_roll

        if track_element.is_junction:
            track_entity.p3 = track_element.p3
            track_entity.p3_roll = track_element.p3_roll

            track_entity.cv3 = track_element.cv3
            track_entity.cv4 = track_element.cv4

            track_entity.p4 = track_element.p4
            track_entity.p4_roll = track_element.p4_roll

        track_entity.radius1 = track_element.radius1
        track_entity.radius2 = track_element.radius2

        track_entity.velocity = track_element.velocity

        track_entity.event0_name = track_element.event0
        track_entity.event1_name = track_element.event1
        track_entity.event2_name = track_element.event2

        track_entity.eventall0_name = track_element.eventall0
        track_entity.eventall1_name = track_element.eventall1
        track_entity.eventall2_name = track_element.eventall2

        track_entity.isolated_name = track_element.isolated
        track_entity.overhead = track_element.overhead

        track_entity.angle1 = track_element.angle1
        track_entity.angle2 = track_element.angle2

        track_entity.fouling1 = track_element.fouling1
        track_entity.fouling2 = track_element.fouling2

        track_entity.railprofile = track_element.railprofile

        track_entity.friction_memcell = track_element.friction_memcell_name