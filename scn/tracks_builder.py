from pathlib import Path
import math

import bmesh
import mathutils
import bpy
import eu07_tools
from ..common import create_material_from_path
from .utils import get_materials_for_trajectory


def generate_trajectory_profile(trajectory_type, profile_params, trajectory_width, mapping_length):
    generator = None
    
    if trajectory_type == "normal":
        generator = TrackProfileGenerator()
    else if trajectory_type == "road":
        generator = RoadProfileGenerator()
    else if (trajectory_type == "river"):
        generator = RiverProfileGenerator()

    return generator.generate_profile(trajectory_type, profile_params, trajectory_width, mapping_length)


def instantiate_trajectory_profile(self, track_subtype, profile_params, trajectory_width, mapping_length):
    mapping_length = 6
    name = get_profile_name(track_subtype, profile_params, trajectory_width, mapping_length)
    profile = bpy.data.objects.get(name)
    if (profile is None):
        profile = generate_trajectory_profile(track_subtype, profile_params, trajectory_width, mapping_length)

    profile = profile.copy()
    bpy.context.scene.collection.objects.link(profile)

    return profile


def get_profile_name(track_subtype, profile_params, trajectory_width, mapping_length):
    return f"TProfile_{self.typename}_{'-'.join(str(x) for x in profile_params)}_ML{mapping_length}_{trajectory_width}"


class TrajectoryBuilder:
    def __init__(self, config):
        self._config = config
        self.default_node_track = eu07_tools.scn.create_element("node:track")

    def build_trajectory(self, track):
        if (track.subtype != "normal"):
            return
        track_object = self.create_trajectory(track.name)
       
        bpy.context.scene.collection.objects.link(track_object)

       
        if track.is_junction:
            junction_track = create_trajectory(track.name)
            bpy.context.scene.collection.objects.link(junction_track)
            junction_track.scn_properties.type_ = track.type + ":" + track.subtype
            junction_track.parent = track_object
            junction_track.location = (0,0,0)
            
            self._create_spline(junction_track, track.p3, track.cv3, track.p4, track.cv4)


        

        materials = get_materials_for_trajectory([track.map1, track.map2], self._config["asset_searcher"])


    def create_trajectory(node_track=self.default_node_track):
        trajectory = bpy.data.objects.new(node_track.name, bpy.data.curves.new(node_track.name, 'CURVE'))
        traectory.data.dimensions = "3D"
        trajectory.data.use_stretch = True
        trajectory.data.use_deform_bounds = True
        trajectory.location = eu07_tools.utils.switch_coordinate_system(track.p1)

        trajectory.scn_properties.type_ = node_track.type + ":" + node_track.subtype
        trajectory.scn_properties.node_max_distance = node_track.max_distance
        trajectory.scn_properties.node_min_distance = node_track.min_distance
        trajectory.scn_properties.trajectory_width = node_track.width
        trajectory.scn_properties.trajectory_friction = node_track.friction
        trajectory.scn_properties.trajectory_sound_distance = node_track.sound_distance
        trajectory.scn_properties.trajectory_quality = node_track.quality_flag
        trajectory.scn_properties.trajectory_damage = node_track.damage_flag
        trajectory.scn_properties.trajectory_environment = node_track.environment
        trajectory.scn_properties.trajectory_visible = node_track.is_visible
        trajectory.scn_properties.trajectory_mapping_length = node_track.mapping_length
        trajectory.scn_properties.trajectory_p1_roll = node_track.p1_roll
        trajectory.scn_properties.trajectory_p2_roll = node_track.p2_roll
        trajectory.scn_properties.trajectory_event0 = node_track.event0
        trajectory.scn_properties.trajectory_event1 = node_track.event1
        trajectory.scn_properties.trajectory_event2 = node_track.event2
        trajectory.scn_properties.trajectory_eventall0 = node_track.eventall0
        trajectory.scn_properties.trajectory_eventall1 = node_track.eventall1
        trajectory.scn_properties.trajectory_eventall2 = node_track.eventall2
        trajectory.scn_properties.trajectory_isolated = node_track.isolated
        trajectory.scn_properties.trajectory_overhead = node_track.overhead
        trajectory.scn_properties.trajectory_angle1 = node_track.angle1
        trajectory.scn_properties.trajectory_angle2 = node_track.angle2
        trajectory.scn_properties.trajectory_fouling1 = node_track.fouling1
        trajectory.scn_properties.trajectory_fouling2 = node_track.fouling2
        trajectory.scn_properties.trajectory_vradius = node_track.vradius
        trajectory.scn_properties.trajectory_railprofile = node_track.railprofile
        trajectory.scn_properties.trajectory_friction_memcell_name = node_track.friction_memcell_name

        profile = self.instantiate_trajectory_profile(node_track.subtype, node_track.geometry_params, node_track.width, node_track.mapping_length)

        self._create_spline(trajectory, node_track.p1, node_track.cv1, node_track.p2, node_track.cv2)


    def _create_spline(self, obj, p1, cv1, p2, cv2):
        spline = obj.data.splines.new('BEZIER')
        spline.use_smooth = False
        
        spline.bezier_points.add(1)
        spline.bezier_points[0].co = (0,0,0)
        spline.bezier_points[0].handle_left = (0,0,0)
        spline.bezier_points[0].handle_right = eu07_tools.utils.switch_coordinate_system(cv1)
        if (cv1 == (0,0,0)):
            spline.bezier_points[0].handle_left_type = 'AUTO' 
            spline.bezier_points[0].handle_right_type = 'AUTO' 

        p2 = p2 - p1
        spline.bezier_points[1].co = eu07_tools.utils.switch_coordinate_system(p2) 
        spline.bezier_points[1].handle_right = eu07_tools.utils.switch_coordinate_system(p2)
        spline.bezier_points[1].handle_left = eu07_tools.utils.switch_coordinate_system(p2 + cv2)  
        if (cv2 == (0,0,0)):
            spline.bezier_points[1].handle_left_type = 'AUTO' 
            spline.bezier_points[1].handle_right_type = 'AUTO' 

        return spline


class TrajectoryProfileGenerator:
    def __init__(self):
        self.object = None
        self.mesh = None
        self.uv_layer = None
        self.typename = ""

    def generate_profile(self, track_subtype, profile_params, trajectory_width, mapping_length):
        self.object = bpy.data.objects.new(make_name(), bpy.data.meshes.new(make_name()))
        bpy.data.collections["Profiles"].objects.link(profile)

        for i in range(2):
            self.object.data.materials.append(None)
            self.object.material_slots[i].link = 'OBJECT'

        array_mod = self.object.modifiers.new('Array', type='ARRAY')
        array_mod.fit_type = 'FIT_CURVE'
        curve_mod = self.object.modifiers.new('Curve', type='CURVE')

        self.mesh = bmesh.new()
        self.uv_layer =  mesh.loops.layers.uv.new()

        self._build_mesh(profile_params, trajectory_width, mapping_length)

        self.mesh.to_mesh(self.object.data)
        self.mesh.free()

    def _build_mesh(profile_params, trajectory_width, mapping_length):
        pass
        

    def _make_face(vertices, uv):
            vertices[2:] = reversed(vertices[2:])

            face = self.mesh.faces.new(vertices)
            face.material_index = 1

            for vertex_index, loop in enumerate(face.loops):
                loop[uv_layer].uv = uv[vertex_index]



class TrackProfileGenerator(TrajectoryProfileGenerator):
    def __init__(self):
        super().__init__()

    def _build_mesh(profile_params, trajectory_width, mapping_length):
        max_z = profile_params[0]
        med_y = trajectory_width/2 + profile_params[1]
        max_y = med_y + profile_params[2]
        segment_length = mapping_length

        #self.generate_rails(mesh, uv_layer, mapping_length, trajectory_width)

        verts_co = [
            self.mesh.verts.new((-segment_length/2, max_y, -max_z)),
            self.mesh.verts.new((segment_length/2, max_y, -max_z)),
            self.mesh.verts.new((-segment_length/2, med_y, 0)),
            self.mesh.verts.new((segment_length/2, med_y, 0)),
            self.mesh.verts.new((-segment_length/2, -med_y, 0)),
            self.mesh.verts.new((segment_length/2, -med_y, 0)),
            self.mesh.verts.new((-segment_length/2, -max_y, -max_z)),
            self.mesh.verts.new((segment_length/2, -max_y, -max_z)),
        ]

        slope_uv_length = math.sqrt(profile_params[2] ** 2 + max_z ** 2)/mapping_length
        med_u = med_y/mapping_length
        max_u = slope_uv_length + med_u

        verts_uv = [
            (0.5 + max_u, 0),
            (0.5 + max_u, 1),
            (med_u + 0.5, 1),
            (med_u + 0.5, 0),
            (0.5 - med_u, 0),
            (0.5 - med_u, 1),
            (0.5 - max_u, 1),
            (0.5 - max_u, 0)
        ]

        for i in range(3):
            vindex_start, vindex_end = i*2, i*2+4
            vertices = verts_co[vindex_start:vindex_end]
            uvs = verts_uvs[vindex_start:vindex_end] 

            self,_make_face(vertices, uv)
            


    def generate_rails(self, mesh, uv_layer, mapping_length, spacing):
        height = 0.15
        width = 0.067

        profile = [
            (0, 0, 0),
            (0, 0, height),
            (0, width, height),
            (0, width, 0),
        ]

        # u coordinates 
        u_co = [
            0,
            0.25,
            0.65,
            1 
        ]

        vertices = []

        for i in range(2):
            sideX = 1 if i == 0 else -1

            faceverts = []
            faceus = []

            for vindex, pv in enumerate(profile):
                v = mathutils.Vector(pv)
                v = v + mathutils.Vector((0, sideX * spacing/2, 0))
                faceverts.append(self.mesh.verts.new(v - mathutils.Vector((-mapping_length/2, 0, 0))))
                faceverts.append(self.mesh.verts.new(v + mathutils.Vector((-mapping_length/2, 0, 0))))
                faceus.append(u_co[vindex]),
                faceus.append(u_co[vindex])
        
            for i in range(3):

                vindex_start, vindex_end = i*2, i*2+4
                vertices = faceverts[vindex_start:vindex_end]
                us = faceus[vindex_start:vindex_end]

                vertices[:2] = reversed(vertices[:2])
                us[:2] = reversed(us[:2])

                face = self.mesh.faces.new(vertices)
                face.material_index = 0

                for vertex_index, loop in enumerate(face.loops):
                    v = mapping_length / 2
                    if face.verts[vertex_index].co.x < 0:
                        v *= -1

                    loop[uv_layer].uv = (us[vertex_index], v)
                

class RoadProfileGenerator(TrajectoryProfileGenerator):
    pass

class RiverProfileGenerator(TrajectoryProfileGenerator):
    pass


                

                
                    

                

    

