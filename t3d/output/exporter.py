import pathlib

import bpy

import eu07_tools
from common.utils import get_environment_path
from common import includes
from common.export_manager import ExportManager
from . import output_builders


class T3DExporter:
    def __init__(self):
        self.objects_range = "ALL"
        self.apply_modifiers = True
        self.aggregate_includes = False
        self.embed_skins = False
        self.remove_name_suffixes = False
        self.use_generated_img_name = False

    def export_to_file(self, filepath):
        export_manager = ExportManager(bpy.context.scene.eu07_includes, self.aggregate_includes)
        export_manager.create_buffers()
        export_manager.create_outputs(eu07_tools.t3d.T3DOutput)

        objects_to_export = self._get_objects()

        identifiers_written_includes = set()

        for obj in objects_to_export:
            if len(obj.material_slots) <= 1: # TODO: Get by unique materials
                submodels = self._create_submodel(obj)
            else:
                submodels = self._create_submodels_from_multimaterial(obj)
            if not submodels:
                continue

            if not self.aggregate_includes and (obj.eu07_include_identifier != includes.MASTER_IDENTIFIER):
                if obj.eu07_include_identifier not in identifiers_written_includes:
                    include = includes.get_include_by_identifier(obj.eu07_include_identifier)
                    include_element = eu07_tools.t3d.create_include(include.file_path, [])

                    export_manager.master_output.dump_element(include_element)

                    identifiers_written_includes.add(obj.eu07_include_identifier)

            identifier = includes.MASTER_IDENTIFIER if self.aggregate_includes else obj.eu07_include_identifier

            output = export_manager.get_output(identifier)

            if output:
                output.dump_from_iterable(submodels)

        # HACK: To make external-environment export possible, we need to do this...
        try:
            environment_path = get_environment_path()
        except ValueError:
            environment_path = pathlib.Path(filepath).parent

        export_manager.flush_buffers_to_files(environment_path, filepath)

    def _get_objects(self):
        objects = bpy.context.scene.objects
        if self.objects_range == "SELECTION":
            objects = bpy.context.selected_objects
        elif self.objects_range == "VISIBLE":
            objects = bpy.context.visible_objects
        elif self.objects_range == "ACTIVE_COLLECTION":
            objects = bpy.context.collection.objects

        for obj in objects:
            is_root = (obj.parent is None or obj.parent not in objects)

            if is_root:
                yield obj
                for child in obj.children_recursive:
                    yield child

    def _create_submodel(self, obj):
        builder = output_builders.get_builder(obj)
        if not builder:
            return None

        builder.set_name(remove_name_suffixes=self.remove_name_suffixes)
        builder.set_parent_name(remove_name_suffixes=self.remove_name_suffixes)
        builder.set_diffuse_color()
        builder.set_anim()
        builder.set_selfillum()
        builder.set_max_distance()
        builder.set_min_distance()
        builder.set_transform()

        submodel_type = builder.submodel.type

        if submodel_type == "Mesh":
            builder.set_ambient_color()
            builder.set_specular_color()
            builder.set_wire()
            builder.set_wire_size()
            builder.set_opacity()
            builder.set_map(embed_skins=self.embed_skins, use_generated_img_name=self.use_generated_img_name)
            builder.set_geometry(apply_modifiers=self.apply_modifiers)
        elif submodel_type == "FreeSpotLight":
            builder.set_near_atten_start()
            builder.set_near_atten_end()
            builder.set_use_near_atten()
            builder.set_far_atten_decay_type()
            builder.set_far_decay_radius()
            builder.set_falloff_angle()
            builder.set_hotspot_angle()
        elif submodel_type == "Stars":
            builder.set_points()

        return [builder.submodel]

    def _create_submodels_from_multimaterial(self, obj):
        banan_builder = output_builders.BananMeshOutputBuilder(obj)
        banan_builder.set_name(remove_name_suffixes=self.remove_name_suffixes)
        banan_builder.set_parent_name(remove_name_suffixes=self.remove_name_suffixes)
        banan_builder.set_ambient_color()
        banan_builder.set_diffuse_color()
        banan_builder.set_specular_color()
        banan_builder.set_anim()
        banan_builder.set_selfillum()
        banan_builder.set_wire()
        banan_builder.set_wire_size()
        banan_builder.set_opacity()
        banan_builder.set_max_distance()
        banan_builder.set_min_distance()
        banan_builder.set_transform()

        banan = banan_builder.submodel

        submodels = [banan]

        for material_slot in obj.material_slots:
            child_builder = output_builders.MeshOutputBuilder(obj)
            child_builder.set_name(
                name=f"{obj.name}_m{material_slot.slot_index}"
            )
            child_builder.set_parent_name(override=banan.name)
            child_builder.set_ambient_color(override=banan.ambient_color)
            child_builder.set_diffuse_color(override=banan.diffuse_color)
            child_builder.set_specular_color(override=banan.specular_color)
            child_builder.set_anim(override=banan.anim)
            child_builder.set_selfillum(override=banan.selfillum)
            child_builder.set_wire(override=banan.wire)
            child_builder.set_wire_size(override=banan.wire_size)
            child_builder.set_opacity(override=banan.opacity)
            child_builder.set_max_distance(override=-1) # TODO: Kill magic number?
            child_builder.set_map(
                material_override=material_slot.material,
                embed_skins=self.embed_skins,
                use_generated_img_name=self.use_generated_img_name
            )
            child_builder.set_geometry(
                material_index=material_slot.slot_index,
                apply_modifiers=self.apply_modifiers
            )

            submodels.append(child_builder.submodel)

        return submodels