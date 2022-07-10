from datetime import datetime
import pathlib

import bpy
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ExportHelper
import eu07_tools

from common.export_manager import ExportManager
from common import utils

import bpy
import bmesh

from collections.abc import Iterable

from material_tools.utils import get_shortpath_from_material


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
        export_manager = ExportManager(bpy.context.scene.eu07_includes)
        export_manager.create_buffers()
        export_manager.create_outputs(eu07_tools.scn.SCNOutput)

        for buffer in export_manager.buffers:
            export_date = datetime.now().strftime("%d/%m/%Y %H:%M")
            buffer.write(f"// Exported from BlendSCN Editor {export_date}\n\n")

        # export_manager.master_output.dump_element(config.get_config_as_element())

        for include in bpy.context.scene.eu07_includes:
            include_element = eu07_tools.scn.create_element("include")
            include_element.path = str(pathlib.Path(include.file_path).relative_to("scenery"))

            export_manager.master_output.dump_element(include_element)

        export_manager.master_buffer.write("\n")

        if self.use_selection:
            objects = [o for o in bpy.data.objects if o.select_get()]
        else:
            objects = bpy.data.objects

        for obj in objects:
            print(f"Exporting {obj} to SCN")
            output = export_manager.get_output(obj.eu07_include_identifier)

            element = self._create_element_from_object(obj)

            if isinstance(element, Iterable):
                for el in element:
                    output.dump_element(el)
            else:
                output.dump_element(element)

        # export_manager.master_buffer.write(firstinit.get_firstinit())

        export_manager.flush_buffers_to_files(utils.get_environment_path(), self.filepath)

        return {'FINISHED'}

    def _create_element_from_object(self, obj):
        element = None
        if "node:track" in obj.eu07_scn_entity_type:
            element = self._create_node_track(obj)
        elif "node:triangles" in obj.eu07_scn_entity_type:
            element = self._create_node_triangles(obj)
        elif "node:model" in obj.eu07_scn_entity_type:
            element = self._create_node_model(obj)
        elif "node:lines" in obj.eu07_scn_entity_type:
            element = self._create_node_lines(obj)

        return element


    def _create_node_triangles(self, terrain_object):
        depsgraph = bpy.context.evaluated_depsgraph_get()
        obj_eval = terrain_object.evaluated_get(depsgraph)

        mesh = bpy.data.meshes.new_from_object(obj_eval)
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        bm.to_mesh(mesh)
        bm.free()

        uv_layer = mesh.uv_layers.active
        if uv_layer:
            uv_data = uv_layer.data[:]

        mesh.validate_material_indices()
        mesh.calc_normals_split()
        for polygon in mesh.polygons:
            node = eu07_tools.scn.create_element("node:triangles")

            try:
                material = mesh.materials[polygon.material_index]
            except IndexError:
                pass
            else:
                node.map = get_shortpath_from_material(material)

            for loop_index in polygon.loop_indices:
                loop = mesh.loops[loop_index]

                xyz = eu07_tools.utils.swizzle_coords(terrain_object.matrix_world @ mesh.vertices[loop.vertex_index].co)
                ijk = eu07_tools.utils.swizzle_coords(loop.normal)
                uv = uv_data[loop_index].uv if uv_layer else [0, 0]

                node.vertices.new((*xyz, *ijk, *uv))
            yield node

        bpy.data.meshes.remove(mesh)

    def _create_node_track(self, obj):
        track = eu07_tools.scn.create_element("node:track")

        tp = obj.eu07_track

        track.name = tp.name
        track.max_distance = tp.max_distance
        track.min_distance = tp.min_distance
        track.subtype = tp.type
        track.length = tp.length
        track.width = tp.width
        track.friction = tp.friction
        track.sound_distance = tp.sound_distance
        track.quality_flag = tp.quality_flag
        track.damage_flag = tp.damage_flag
        track.environment = tp.environment
        track.is_visible = (tp.visibility == "vis")
        track.map1 = tp.get_map1()
        track.map2 = tp.get_map2()
        track.mapping_length = tp.map1_length
        track.geometry_params = tp.geometry_params

        track.p1 = tp.p1
        track.p1.swizzle()
        track.p1_roll = tp.p1_roll

        track.cv1 = tp.get_cv1_local()
        track.cv1.swizzle()

        track.cv2 = tp.get_cv2_local()
        track.cv2.swizzle()

        track.p2 = tp.p2
        track.p2.swizzle()
        track.p2_roll = tp.p2_roll

        track.radius1 = tp.radius1

        track.p3 = tp.p3
        track.p3.swizzle()
        track.p3_roll = tp.p3_roll

        track.cv3 = tp.get_cv3_local()
        track.cv3.swizzle()

        track.cv4 = tp.get_cv4_local()
        track.cv4.swizzle()

        track.p4 = tp.p4
        track.p4.swizzle()
        track.p4_roll = tp.p4_roll

        track.radius2 = tp.radius2

        track.velocity = tp.velocity
        track.event0 = tp.event0_name
        track.event1 = tp.event1_name
        track.event2 = tp.event2_name
        track.eventall0 = tp.eventall0_name
        track.eventall1 = tp.eventall1_name
        track.eventall2 = tp.eventall2_name
        track.isolated = tp.isolated_name
        track.overhead = tp.overhead
        track.angle1 = tp.angle1
        track.angle2 = tp.angle2
        track.fouling1 = tp.fouling1
        track.fouling2 = tp.fouling2
        track.railprofile = tp.railprofile
        track.friction_memcell_name = tp.friction_memcell
        track.trackbed = tp.get_switch_trackbed_map()

        return track


    def _create_node_model(self, obj):
        model = eu07_tools.scn.create_element("node:model")

        mp = obj.eu07_scn_model

        model.name = mp.name
        model.max_distance = mp.max_distance
        model.min_distance = mp.min_distance
        model.location = mp.location
        model.location.swizzle()
        model.rotation = mp.rotation
        model.rotation.swizzle()
        model.path = mp.model_path
        # TODO: Lights, light states, replacableskins
        model.notransition = mp.notransition

        return model

    def _create_node_lines(self, obj):
        lines = eu07_tools.scn.create_element("node:lines")

        lp = obj.eu07_scn_lines

        lines.name = lp.name
        lines.max_distance = lp.max_distance
        lines.min_distance = lp.min_distance
        lines.thickness = lp.thickness * 100
        lines.color = lp.color * 255

        for spline in obj.data.splines:
            first_index = 0
            last_index = len(spline.bezier_points) - 1
            for point_idx, point in enumerate(spline.bezier_points):
                co = obj.matrix_world @ point.co
                point1 = lines.points.new(co)
                point1.swizzle()
                if point_idx not in (first_index, last_index):
                    point2 = lines.points.new(co)
                    point2.swizzle()

        return lines