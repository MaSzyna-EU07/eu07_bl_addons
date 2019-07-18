import bpy
import bmesh

# This is spaghetti, written for experimental purposes - needs to be refactored

def to_scn_coords(vector):
    return (-vector.x, vector.z, vector.y)


class SceneryBuilder:
    def __init__(self):
        self._terrain_builder = _TerrainBuilder()
        self._tracks_builder = _TracksBuilder()

    def run(self, data):
        for element in data:
            if element.typename == "node:triangles":
                self._terrain_builder.add_triangle(element)
            elif "node:track" in element.typename:
                self._tracks_builder.add_curve(element)

        self._terrain_builder.finish()


class _TracksBuilder:
    def __init__(self):
        self._tracks_object = bpy.data.objects.new("tracks", bpy.data.curves.new("tracks", 'CURVE'))
        bpy.context.scene.collection.objects.link(self._tracks_object)
        self._tracks_object.data.dimensions = '3D'

    def add_curve(self, element):
        subtype = element.typename.split(":")[-1]
        
        for segment in element.segments:
            spline = self._tracks_object.data.splines.new('BEZIER')

            spline.bezier_points.add(1)
            spline.bezier_points[0].co = to_scn_coords(segment.p1)
            spline.bezier_points[0].handle_left = to_scn_coords(segment.p2)
            spline.bezier_points[0].handle_right = to_scn_coords(segment.p1 + segment.cv1)
    
            spline.bezier_points[1].co = to_scn_coords(segment.p2) 
            spline.bezier_points[1].handle_right = to_scn_coords(segment.p2)
            spline.bezier_points[1].handle_left = to_scn_coords(segment.p2 + segment.cv2)


class _TerrainBuilder:
    def __init__(self):
        self._terrain_mesh = bmesh.new()
        self._terrain_object = bpy.data.objects.new("terrain", bpy.data.meshes.new("terrain"))
        bpy.context.scene.collection.objects.link(self._terrain_object)

        self._materials_buffer = [

        ]

    def add_triangle(self, element):
        num_triangles = len(element.vertices) // 3

        for triangle_idx in range(num_triangles):
            vertices = element.vertices[
                triangle_idx * 3 : triangle_idx * 3 + 3
            ]

            bm_face_verts = []
            for vertex in vertices:
                bm_vert = self._terrain_mesh.verts.new(to_scn_coords(vertex.location))
                bm_face_verts.append(bm_vert)

            bm_face = self._terrain_mesh.faces.new(bm_face_verts)

    def finish(self):
        # remove doubles?
        self._terrain_mesh.to_mesh(self._terrain_object.data)
        self._terrain_mesh.free()
            