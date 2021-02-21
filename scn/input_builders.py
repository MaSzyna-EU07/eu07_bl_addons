from pathlib import Path
import math

import bmesh
import mathutils
import bpy
import eu07_tools
from ..common import create_material_from_path
from .utils import get_materials_for_trajectory

# This is spaghetti, written for experimental purposes - needs to be refactored

class SceneryBuilder:
    def __init__(self, config):
        self._terrain_builder = _TerrainBuilder(config)
        self._tracks_builder = _TracksBuilder(config)
        self._lines_builder = _LinesBuilder(config)

    def run(self, data):
        for element in data:
            if element.type == "node:triangles":
                self._terrain_builder.add_triangle(element)
            elif element.type == "node:track":
                self._tracks_builder.build_trajectory(element)
            elif element.type == "node:lines":
                self._lines_builder.add_line(element)
            elif element.type == "include":
                if (element.path.endswith(".inc")):
                    pass
        self._terrain_builder.finish()
        self._lines_builder.finish()


class _LinesBuilder:
    def __init__(self, config):
        self._config = config
        self._lines_mesh = bmesh.new()
        self._lines_object = bpy.data.objects.new("lines", bpy.data.meshes.new("lines"))
        bpy.context.scene.collection.objects.link(self._lines_object)

    def add_line(self, lines_node):
        edge_verts = []

        if lines_node.subtype == "normal":
            pass

        else:
            for point in lines_node.points:
                bm_vert = self._lines_mesh.verts.new(eu07_tools.utils.switch_coordinate_system(point))
                edge_verts.append(bm_vert)

                if len(edge_verts) == 2:
                    bm_edge = self._lines_mesh.edges.new(edge_verts)
                    edge_verts.pop(0)
            
            if lines_node.subtype == "loop":
                self._lines_mesh.verts.ensure_lookup_table()
                # close da loop
                bm_edge = self._lines_mesh.edges.new((
                    self._lines_mesh.verts[0],
                    self._lines_mesh.verts[-1]
                ))

    def finish(self):
        self._lines_mesh.to_mesh(self._lines_object.data)
        self._lines_mesh.free()

class _TracksBuilder:
    def __init__(self, config):
        self._config = config

    def build_trajectory(self, track):
        if (track.subtype != "normal"):
            return
        track_object = bpy.data.objects.new(track.name, bpy.data.curves.new(track.name, 'CURVE'))
        track_object.location = eu07_tools.utils.switch_coordinate_system(track.p1)
        track_object.scn_properties.type_ = track.type + ":" + track.subtype
        bpy.context.scene.collection.objects.link(track_object)

        track_object.scn_properties.node_max_distance = track.max_distance
        track_object.scn_properties.node_min_distance = track.min_distance
        track_object.scn_properties.trajectory_width = track.width
        track_object.scn_properties.trajectory_friction = track.friction
        track_object.scn_properties.trajectory_sound_distance = track.sound_distance
        track_object.scn_properties.trajectory_quality = track.quality_flag
        track_object.scn_properties.trajectory_damage = track.damage_flag
        track_object.scn_properties.trajectory_environment = track.environment
        track_object.scn_properties.trajectory_visible = track.is_visible
        track_object.scn_properties.trajectory_mapping_length = track.mapping_length
        track_object.scn_properties.trajectory_p1_roll = track.p1_roll
        track_object.scn_properties.trajectory_p2_roll = track.p2_roll
        track_object.scn_properties.trajectory_event0 = track.event0
        track_object.scn_properties.trajectory_event1 = track.event1
        track_object.scn_properties.trajectory_event2 = track.event2
        track_object.scn_properties.trajectory_eventall0 = track.eventall0
        track_object.scn_properties.trajectory_eventall1 = track.eventall1
        track_object.scn_properties.trajectory_eventall2 = track.eventall2
        track_object.scn_properties.trajectory_isolated = track.isolated
        track_object.scn_properties.trajectory_overhead = track.overhead
        track_object.scn_properties.trajectory_angle1 = track.angle1
        track_object.scn_properties.trajectory_angle2 = track.angle2
        track_object.scn_properties.trajectory_fouling1 = track.fouling1
        track_object.scn_properties.trajectory_fouling2 = track.fouling2
        track_object.scn_properties.trajectory_vradius = track.vradius
        track_object.scn_properties.trajectory_railprofile = track.railprofile
        track_object.scn_properties.trajectory_friction_memcell_name = track.friction_memcell_name

        track_object.data.dimensions = "3D"
        track_object.data.use_stretch = True
        track_object.data.use_deform_bounds = True

        self._create_spline(track_object, track.p1, track.cv1, track.p2, track.cv2)

        if track.is_junction:
            junction_track = bpy.data.objects.new(track.name, bpy.data.curves.new(track.name, 'CURVE'))
            bpy.context.scene.collection.objects.link(junction_track)
            junction_track.scn_properties.type_ = track.type + ":" + track.subtype
            junction_track.parent = track_object
            junction_track.location = (0,0,0)
            
            junction_track.data.dimensions = "3D"
            junction_track.data.use_stretch = True
            junction_track.data.use_deform_bounds = True

            self._create_spline(junction_track, track.p3, track.cv3, track.p4, track.cv4)

            tprofile = bpy.data.objects.get("TProfile_2-5-13").copy()
            bpy.context.scene.collection.objects.link(tprofile)
            tprofile.parent = junction_track
            tprofile.location = (0,0,0)
            tprofile.hide_select = True
            
            tprofile.modifiers["Array"].curve = junction_track
            tprofile.modifiers["Curve"].object = junction_track

        tprofile = self.instantiate_trajectory_profile(track.subtype, track.geometry_params, track.width, track.mapping_length)

        tprofile.parent = track_object
        tprofile.location = (0,0,0)
        tprofile.hide_select = True

        materials = get_materials_for_trajectory([track.map1, track.map2], self._config["asset_searcher"])

        tprofile.material_slots[0].material = materials[0]
        tprofile.material_slots[1].material = materials[1]
        
        tprofile.modifiers["Array"].curve = track_object
        tprofile.modifiers["Curve"].object = track_object


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

    def instantiate_trajectory_profile(self, track_subtype, profile_params, trajectory_width, mapping_length):
        profile = None
        if (track_subtype in "normal switch"):
            rail_height = 0.15
            mapping_length = 6
            name = f"BallastProfile_{'-'.join(str(x) for x in profile_params)}_ML{mapping_length}_{trajectory_width*1000}mm"
            profile = bpy.data.objects.get(name)
            if (profile is None):
                mesh = bmesh.new()
                uv_layer =  mesh.loops.layers.uv.new()
                profile = bpy.data.objects.new(name, bpy.data.meshes.new(name))
                bpy.data.collections["Profiles"].objects.link(profile)

                array_mod = profile.modifiers.new('Array', type='ARRAY')
                array_mod.fit_type = 'FIT_CURVE'

                curve_mod = profile.modifiers.new('Curve', type='CURVE')

                self.generate_rails(mesh, mapping_length, trajectory_width)

                max_z = profile_params[0]
                med_y = trajectory_width/2 + profile_params[1]
                max_y = med_y + profile_params[2]
                segment_length = mapping_length

                verts_co = [
                    mesh.verts.new((segment_length/2, max_y, -max_z)),
                    mesh.verts.new((-segment_length/2, max_y, -max_z)),
                    mesh.verts.new((-segment_length/2, med_y, 0)),
                    mesh.verts.new((segment_length/2, med_y, 0)),
                    mesh.verts.new((segment_length/2, -med_y, 0)),
                    mesh.verts.new((-segment_length/2, -med_y, 0)),
                    mesh.verts.new((-segment_length/2, -max_y, -max_z)),
                    mesh.verts.new((segment_length/2, -max_y, -max_z)),
                ]

                slope_uv_length = math.sqrt(profile_params[2] ** 2 + max_z ** 2)/mapping_length
                med_u = med_y/mapping_length
                max_u = slope_uv_length + med_u

                verts_uvs = [
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
                    
                    if (i == 1):
                        vertices.reverse()

                    face = mesh.faces.new(vertices)
                    face.material_index = 1

                    for vertex_index, loop in enumerate(face.loops):
                        loop[uv_layer].uv = uvs[vertex_index]
                    

                mesh.to_mesh(profile.data)
                mesh.free()

                for i in range(2):
                    profile.data.materials.append(None)
                    profile.material_slots[i].link = 'OBJECT'

            profile = profile.copy()
            bpy.context.scene.collection.objects.link(profile)

        return profile

    def generate_rails(self, mesh, mapping_length, spacing):
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
            0.4,
            0.6,
            1 
        ]

        vertices = []

        for i in range(2):
            sideX = 1 if i == 0 else -1

            faceverts = []

            for pv in profile:
                v = mathutils.Vector(pv)
                v = v + mathutils.Vector((0, sideX * spacing/2, 0))
                faceverts.append(mesh.verts.new(v - mathutils.Vector((-mapping_length/2, 0, 0))))
                faceverts.append(mesh.verts.new(v + mathutils.Vector((-mapping_length/2, 0, 0))))
        
            for i in range(3):

                vindex_start, vindex_end = i*2, i*2+4
                vertices = faceverts[vindex_start:vindex_end]

                vertices[:2] = reversed(vertices[:2])

                face = mesh.faces.new(vertices)
                face.material_index = 0





class _TerrainBuilder:
    def __init__(self, config):
        self._config = config
        self._terrain_mesh = bmesh.new()
        self._uv_layer = self._terrain_mesh.loops.layers.uv.new()
        self._terrain_object = bpy.data.objects.new("terrain", bpy.data.meshes.new("terrain"))
        bpy.context.scene.collection.objects.link(self._terrain_object)

        self._maps = []

    def add_triangle(self, element):
        num_triangles = len(element.vertices) // 3


        try:
            material_index = self._maps.index(element.map)
        except ValueError:
            self._maps.append(element.map)
            material_index = len(self._maps) - 1

        for triangle_idx in range(num_triangles):
            vertices = element.vertices[
                triangle_idx * 3 : triangle_idx * 3 + 3
            ]

            bm_face_verts = []
            for vertex in vertices:
                bm_vert = self._terrain_mesh.verts.new(eu07_tools.utils.switch_coordinate_system(vertex.location))
                bm_face_verts.append(bm_vert)

            bm_face = self._terrain_mesh.faces.new(bm_face_verts)
            bm_face.material_index = material_index

            for vertex_index, loop in enumerate(bm_face.loops):
                loop[self._uv_layer].uv = vertices[vertex_index].mapping

    def finish(self):
        # remove doubles?
        self._terrain_mesh.to_mesh(self._terrain_object.data)
        self._terrain_mesh.free()


        for map_ in self._maps:
            map_ = map_.lstrip("@").split(":")[0]
            abspath = self._config["asset_searcher"].textures.find(map_)
            material = create_material_from_path(abspath, False)

            self._terrain_object.data.materials.append(material)
