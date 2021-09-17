import bpy
import bmesh
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ExportHelper
import eu07_tools

from .output_builders import create_node_triangles_from_mesh, create_node_track, create_tree_include
import scn


class SCNExporter(bpy.types.Operator, ExportHelper):
    bl_idname = "export_scene.scn"
    bl_label = "Export SCN"
    filename_ext = ".scm"

    filter_glob: StringProperty(
        default="*.scn;*.scm;*.inc",
        options={'HIDDEN'}
    )
    use_selection: BoolProperty(
        name="Use selection",
        default=False
    )

    def execute(self, context):
        with open(self.filepath, mode="w", encoding="windows-1250", newline="\r\n") as outfile:
            if self.use_selection:
                objects = [o for o in bpy.data.objects if o.select_get()]
            else:
                objects = bpy.data.objects

            tracks = []
            for o in objects:
                if 'tree' in o.scn_properties.type_:
                    eu07_tools.scn.dump((create_tree_include(o),), outfile)
                if 'node:sound' in o.scn_properties.type_:
                    eu07_tools.scn.dump((scn.sound.create_element_from_sound(o),), outfile)
                if 'camera' in o.scn_properties.type_:
                    eu07_tools.scn.dump((scn.camera.create_element_from_camera(o),), outfile)
                if 'node:triangles' in o.scn_properties.type_:
                    eu07_tools.scn.dump(create_node_triangles_from_mesh(o.data.copy()), outfile)
                if 'node:track' in o.scn_properties.type_:
                    is_junction_track = (o.parent is not None)
                    if not is_junction_track:
                        tracks.append(create_node_track(o))

            eu07_tools.scn.dump(tracks, outfile)

        return {'FINISHED'}