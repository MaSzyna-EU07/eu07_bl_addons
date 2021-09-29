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

        includes = []
        outfiles = {}
        for scm in context.scene.scm_files:
            out_path = (scenery_dir / scm.file_path)
            out_dir = out_path.parent
            out_dir.mkdir(parents=True, exist_ok=True)
            outfiles[scm.file_index] = self._open_for_writing(out_path)

            include = eu07_tools.scn.create_element("include")
            include.path = scm.file_path
            includes.append(include)

        outfiles[scm_files.MAIN_FILE_INDEX] = self._open_for_writing(self.filepath)

        outputs = {}
        for scm_id, outfile in outfiles.items():
            export_date = datetime.now().strftime("%d/%m/%Y %H:%M")
            outfile.write(f"// Exported from BlendSCN Editor {export_date}\n\n")

            outputs[scm_id] = eu07_tools.scn.SCNOutput(outfile)

        outputs[scm_files.MAIN_FILE_INDEX].dump_from_iterable(includes)

        if self.use_selection:
            objects = [o for o in bpy.data.objects if o.select_get()]
        else:
            objects = bpy.data.objects

        for obj in objects:
            output = outputs.get(obj.scn_properties.scm_file_id)

            if obj.scn_properties.type_ == "node:triangles":
                output.dump_from_iterable(terrain.create_node_triangles_from_mesh(obj))

            else:
                element = self._create_element_from_object(obj)

                if element:
                    output.dump_element(element)

        for outfile in outfiles.values():
            outfile.close()

        return {'FINISHED'}

    def _open_for_writing(self, filepath):
        return open(filepath, mode="w+", encoding="windows-1250", newline="\r\n")

    def _create_element_from_object(self, obj):
        element = None
        if obj.scn_properties.type_ == "tree":
            element = tree_utils.create_tree_include(obj)
        elif obj.scn_properties.type_ == "node:memcell":
            element = memcell.create_memcell_from_object(obj)
        elif obj.scn_properties.type_ == "node:sound":
            element = sound.create_sound_from_object(obj)
        elif obj.scn_properties.type_ == "camera":
            element = camera.create_camera_from_object(obj)
        elif "node:track" in obj.scn_properties.type_:
            element = trajectory_tools.create_element_from_track(obj)

        return element
