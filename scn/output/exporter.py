from datetime import datetime
import pathlib

import bpy
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ExportHelper
import eu07_tools

from common.include_export_manager import IncludeExportManager
from common import utils
from scn import tree_utils, memcell, sound, camera, terrain, trajectory_tools, firstinit, config


class SCNExporter(bpy.types.Operator, ExportHelper):
    bl_idname = "export_scene.scn"
    bl_label = "Export SCN"
    filename_ext = ".scn"

    filter_glob: StringProperty(
        default="*.scn;*.scm;*.inc",
        options={'HIDDEN'}
    )
    use_selection: BoolProperty(
        name="Use selection",
        default=False
    )

    def execute(self, context):
        export_manager = IncludeExportManager(bpy.context.scene.eu07_includes)
        export_manager.create_buffers()
        export_manager.create_outputs(eu07_tools.scn.SCNOutput)

        for buffer in export_manager.buffers:
            export_date = datetime.now().strftime("%d/%m/%Y %H:%M")
            buffer.write(f"// Exported from BlendSCN Editor {export_date}\n\n")

        export_manager.master_output.dump_from_iterable(config.get_config_as_element())

        for include in bpy.context.scene.eu07_includes:
            include_element = eu07_tools.scn.create_element("include")
            include_element.path = str(pathlib.Path(include.file_path).relative_to("scenery"))

            export_manager.master_output.dump_from_iterable(include_element)

        export_manager.master_buffer.write("\n")

        if self.use_selection:
            objects = [o for o in bpy.data.objects if o.select_get()]
        else:
            objects = bpy.data.objects

        for obj in objects:
            output = export_manager.get_output(obj.eu07_include_identifier)

            if obj.scn_properties.type_ == "node:triangles":
                output.dump_from_iterable(terrain.create_node_triangles_from_mesh(obj))

            else:
                element = self._create_element_from_object(obj)
                output.dump_from_iterable(element)

        export_manager.master_buffer.write(firstinit.get_firstinit())

        export_manager.flush_buffers_to_files(utils.get_root(self.filepath), self.filepath)

        return {'FINISHED'}

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
