from datetime import datetime
import pathlib

import bpy
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ExportHelper
import eu07_tools

from common import get_root
from scn import tree_utils, memcell, sound, camera, terrain, trajectory_tools, scm_files


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
        scenery_dir = pathlib.Path(get_root(), "scenery")

        outfiles = {
            scm.file_index: self._open_for_writing(scenery_dir / scm.file_path) for scm in context.scene.scm_files
        }
        outfiles[scm_files.MAIN_FILE_INDEX] = self._open_for_writing(self.filepath)

        outputs = {}
        for scm_id, outfile in outfiles.items():
            outputs[scm_id] = eu07_tools.scn.SCNOutput(outfile)

        for outfile in outfiles:
            export_date = datetime.now().strftime("%d/%m/%Y %H:%M")
            outfile.write(f"// Exported from BlendSCN Editor {export_date}\n\n")

        if self.use_selection:
            objects = [o for o in bpy.data.objects if o.select_get()]
        else:
            objects = bpy.data.objects

        for obj in objects:
            output = outputs.get(obj.scn_properties.scm_file_id)
            element = self._create_element_from_object(obj)

            output.dump_element(element)

        for outfile in outfiles:
            outfile.close()

        return {'FINISHED'}

    def _open_for_writing(self, filepath):
        return open(filepath, mode="w", encoding="windows-1250", newline="\r\n")

    def _create_element_from_object(self, obj):
        if obj.scn_properties.type == "tree":
            element = tree_utils.create_tree_include(obj)
        elif obj.scn_properties.type == "node:memcell":
            element = memcell.create_memcell_from_object(obj)
        elif obj.scn_properties.type == "node:sound":
            element = sound.create_sound_from_object(obj)
        elif obj.scn_properties.type == "camera":
            element = camera.create_camera_from_object(obj)
        elif obj.scn_properties.type == "node:triangles":
            element = terrain.create_node_triangles_from_mesh(obj)
        elif "node:track" in obj.scn_properties.type:
            element = trajectory_tools.create_element_from_track(obj)

        return element
