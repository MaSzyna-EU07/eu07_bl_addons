import bmesh
import bpy
import eu07_tools
from eu07_bl_addons.common import create_material_from_path

# This is spaghetti, written for experimental purposes - needs to be refactored


class SceneryBuilder:
    def __init__(self, config):
        self._terrain_builder = _TerrainBuilder(config)
        self._tracks_builder = _TracksBuilder(config)

    def run(self, data):
        for element in data:
            if element.type == "node:triangles":
                self._terrain_builder.add_triangle(element)
            elif element.type == "node:track":
                self._tracks_builder.add_curve(element)

        self._terrain_builder.finish()


class _TracksBuilder:
    def __init__(self, config):
        self._config = config
        self._last_track_profile = None
        self._tracks_material = bpy.data.materials.new("track")
        self._roads_material = bpy.data.materials.new("road")

    def add_curve(self, track):
        # TODO: Collections for trackbeds
        trackbed_profile = (
        f"{track.geometry_param1}-{track.geometry_param2}-{track.geometry_param3}"
        )

        if track.is_junction:
            trackbed_profile = self._last_track_profile
        else:
            self._last_track_profile = trackbed_profile
        
        tracks_object = bpy.data.objects.get(f"tracks: {trackbed_profile}")

        if not tracks_object:
            tracks_object = bpy.data.objects.new(
                f"tracks: {trackbed_profile}", bpy.data.curves.new(f"tracks: {trackbed_profile}", 'CURVE')
            )
            bpy.context.scene.collection.objects.link(tracks_object)

            trackbed_object = create_trackbed(track, trackbed_profile)

        trackbed_object = bpy.data.objects.get(f"trackbed: {trackbed_profile}")
        tracks_object.data.bevel_object = trackbed_object

        spline = tracks_object.data.splines.new('BEZIER')
        spline.use_smooth = False
        
        spline.bezier_points.add(1)
        spline.bezier_points[0].co = eu07_tools.utils.switch_coordinate_system(track.p1)
        spline.bezier_points[0].handle_left = eu07_tools.utils.switch_coordinate_system(track.p2)
        spline.bezier_points[0].handle_right = eu07_tools.utils.switch_coordinate_system(track.p1 + track.cv1)

        spline.bezier_points[1].co = eu07_tools.utils.switch_coordinate_system(track.p2) 
        spline.bezier_points[1].handle_right = eu07_tools.utils.switch_coordinate_system(track.p2)
        spline.bezier_points[1].handle_left = eu07_tools.utils.switch_coordinate_system(track.p2 + track.cv2)  

        if track.is_junction:
            spline = tracks_object.data.splines.new('BEZIER')
            spline.use_smooth = False

            spline.bezier_points.add(1)
            spline.bezier_points[0].co = eu07_tools.utils.switch_coordinate_system(track.p3)
            spline.bezier_points[0].handle_left = eu07_tools.utils.switch_coordinate_system(track.p3)
            spline.bezier_points[0].handle_right = eu07_tools.utils.switch_coordinate_system(track.p3 + track.cv3)

            spline.bezier_points[1].co = eu07_tools.utils.switch_coordinate_system(track.p4) 
            spline.bezier_points[1].handle_right = eu07_tools.utils.switch_coordinate_system(track.p4)
            spline.bezier_points[1].handle_left = eu07_tools.utils.switch_coordinate_system(track.p4 + track.cv4)


def create_trackbed(track, profile):
    bed_height = track.geometry_param1
    bed_width = track.geometry_param2
    bed_slope = track.geometry_param3
    
    curve = bpy.data.curves.new(f"trackbed: {profile}", 'CURVE')
    obj = bpy.data.objects.new(f"trackbed: {profile}", curve)
    
    obj.location = (0, 0, 0)
    bpy.context.scene.collection.objects.link(obj)
    
    spline = curve.splines.new('BEZIER')
    spline.resolution_u = 1
    spline.resolution_v = 1
    spline.bezier_points.add(3)
    spline.bezier_points[0].co = (track.width/2 + bed_width + bed_slope, 0, 0)
    spline.bezier_points[1].co = (track.width/2 + bed_width, bed_height, 0)
    spline.bezier_points[2].co = (-track.width/2 - bed_width, bed_height, 0)
    spline.bezier_points[3].co = (-track.width/2 - bed_width - bed_slope, 0, 0)

    return obj



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
            material = create_material_from_path(map_, abspath)

            self._terrain_object.data.materials.append(material)
