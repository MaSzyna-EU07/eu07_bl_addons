import bpy
import bmesh

from eu07_bl_addons.common import create_material_from_path

# This is spaghetti, written for experimental purposes - needs to be refactored

def scn_to_xyz_coords(vector):
    return (-vector.x, vector.z, vector.y)


class SceneryBuilder:
    def __init__(self, config):
        self._terrain_builder = _TerrainBuilder(config)
        self._tracks_builder = _TracksBuilder(config)

    def run(self, data):
        for element in data:
            if element.typename == "node:triangles":
                self._terrain_builder.add_triangle(element)
            elif "node:track" in element.typename:
                self._tracks_builder.add_curve(element)

        self._terrain_builder.finish()


class _TracksBuilder:
    def __init__(self, config):
        self._config = config
        self._tracks_object = bpy.data.objects.new("tracks", bpy.data.curves.new("tracks", 'CURVE'))
        bpy.context.scene.collection.objects.link(self._tracks_object)
        self._tracks_object.data.dimensions = '3D'

        self._trackbed_specs = set()

    def add_curve(self, element):
        for segment in element.segments:
            spline = self._tracks_object.data.splines.new('BEZIER')
            spline.use_smooth = False

            spline.bezier_points.add(1)
            spline.bezier_points[0].co = scn_to_xyz_coords(segment.p1)
            spline.bezier_points[0].handle_left = scn_to_xyz_coords(segment.p2)
            spline.bezier_points[0].handle_right = scn_to_xyz_coords(segment.p1 + segment.cv1)
    
            spline.bezier_points[1].co = scn_to_xyz_coords(segment.p2) 
            spline.bezier_points[1].handle_right = scn_to_xyz_coords(segment.p2)
            spline.bezier_points[1].handle_left = scn_to_xyz_coords(segment.p2 + segment.cv2)         



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
                bm_vert = self._terrain_mesh.verts.new(scn_to_xyz_coords(vertex.location))
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
            abspath = self._config["asset_searcher"].textures_finder.find(map_)
            material = create_material_from_path(map_, abspath)

            # This code causes bad material assigns, possibly
            if material is not None:
                self._terrain_object.data.materials.append(material)
            

            


class HashableMaterial:
    def __init__(self, map_, ambient, diffuse, specular):
        self.map = map_
        self.ambient = ambient
        self.specular = specular
        self.diffuse = diffuse
            