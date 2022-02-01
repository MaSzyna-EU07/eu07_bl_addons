import bpy

import eu07_tools
from common.utils import get_environment_path
from common import includes
from common.export_manager import ExportManager
from .hierarchy_maker import HierarchyMaker
from . import output_builders


class T3DExporter:
    def __init__(self):
        self.use_selection = False
        self.apply_modifiers = True
        self.aggregate_includes = False
        self.embed_skins = False

    def export_to_file(self, filepath):
        export_manager = ExportManager(bpy.context.scene.eu07_includes, self.aggregate_includes)
        export_manager.create_buffers()
        export_manager.create_outputs(eu07_tools.t3d.T3DOutput)

        objects_to_export = bpy.context.selected_objects if self.use_selection else bpy.data.objects
        objects_to_export = HierarchyMaker().make_hierarchy(objects_to_export)

        identifiers_written_includes = set()

        for obj in objects_to_export:
            if not self.aggregate_includes and (obj.eu07_include_identifier != includes.MASTER_IDENTIFIER):
                if obj.eu07_include_identifier not in identifiers_written_includes:
                    include = includes.get_include_by_identifier(obj.eu07_include_identifier)
                    include_element = eu07_tools.t3d.create_include(include.file_path, [])

                    export_manager.master_output.dump_element(include_element)

                    identifiers_written_includes.add(obj.eu07_include_identifier)

            identifier = includes.MASTER_IDENTIFIER if self.aggregate_includes else obj.eu07_include_identifier

            output = export_manager.get_output(identifier)
            submodel = self._create_submodel_to_export(obj)

            output.dump_element(submodel)

        export_manager.flush_buffers_to_files(get_environment_path(), filepath)

    def _create_submodel_to_export(self, obj):
        builder = output_builders.get_builder(obj)
        if not builder:
            return None

        builder.set_parent()
        builder.set_diffuse()
        builder.set_anim()
        builder.set_selfillum()
        builder.set_max_distance()
        builder.set_min_distance()
        builder.set_transform()

        submodel_type = builder.submodel.type

        if submodel_type == "Mesh":
            builder.set_ambient()
            builder.set_specular()
            builder.set_wire()
            builder.set_wire_size()
            builder.set_opacity()
            builder.set_map(self.embed_skins)
            builder.set_geometry(self.apply_modifiers)
        elif submodel_type == "FreeSpotLight":
            builder.set_near_atten_start()
            builder.set_near_atten_end()
            builder.set_use_near_atten()
            builder.set_far_atten_decay_type()
            builder.set_far_decay_radius()
            builder.set_falloff_angle()
            builder.set_hotspot_angle()
        elif submodel_type == "Stars":
            builder.set_geometry()

        return builder.submodel