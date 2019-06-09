from pathlib import Path

import bpy
from bpy.props import (
    StringProperty, EnumProperty, BoolProperty, 
    FloatProperty, IntProperty, FloatVectorProperty
)
from bpy_extras.io_utils import ImportHelper, ExportHelper

# HACK: egg import failed
import sys
sys.path.append("/home/krzysiu/Dokumenty/PYTHON/eu07_tools/")
from eu07_tools import t3d
from eu07_tools.utils import AssetSearcher, find_root

from .input_builders import build_object_from_submodel
from .output_builders import build_submodel_from_object


class T3DImport(bpy.types.Operator, ImportHelper):
    bl_idname = "import_model.t3d"
    bl_label = "Import T3D"
    filename_ext = ".t3d"

    filter_glob: StringProperty(
        default="*.t3d",
        options={'HIDDEN'}
    )

    skin_1: StringProperty(
        name="Skin #1",
    )
    skin_2: StringProperty(
        name="Skin #2",
    )
    skin_3: StringProperty(
        name="Skin #3",
    )
    skin_4: StringProperty(
        name="Skin #4",
    )

    default_ext: EnumProperty(
        name="Default texture extension",
        default=".tga",
        items=[
            (".tga", "TGA", ""),
            (".dds", "DDS", ""),
            (".png", "PNG", ""),
            (".dds", "BMP", "")
        ]
    )

    def execute(self, context):
        try:
            root = find_root(self.filepath)
        except ValueError:
            #TODO: Get from script prefs / userprefs
            raise Warning("NO ROOT FOUND!!")


        config = {
            "skins": {
                "replacableskin": self.skin_1,
                "-1": self.skin_1, 
                "-2": self.skin_2, 
                "-3": self.skin_3, 
                "-4": self.skin_4
            },
            "asset_searcher": AssetSearcher(root, Path(self.filepath).parent),
        }

        # NOTE: Temporary mat discarding
        config["asset_searcher"].textures_finder.remove_extension(".mat")
        config["asset_searcher"].textures_finder.set_extension_priority(self.default_ext, 1)

        with open(self.filepath) as infile:
            
            for element in t3d.load(infile):

                if element.element_type == "submodel":
                    build_object_from_submodel(element, config)

                elif element.element_type == "include":
                    # TODO: Includes
                    pass
        return {'FINISHED'}


class T3DExport(bpy.types.Operator, ExportHelper):
    bl_idname = "export_model.t3d"
    bl_label = "Export T3D"
    filename_ext = ".t3d"

    filter_glob: StringProperty(
        default="*.t3d",
        options={'HIDDEN'}
    )

    use_selection: BoolProperty(
        name="Selection Only",
        default=False
    )

    use_modifiers: BoolProperty(
        name="Apply modifiers",
        default=True
    )

    def execute(self, context):
        objects = bpy.context.selected_objects if self.use_selection else bpy.data.objects
        objects = [
            o for o in objects 
            if o.type == 'MESH' or 
            (o.type == 'LIGHT' and o.data.type == 'SPOT') or
            (o.type == 'EMPTY')
        ]

        config = {
            "use_modifiers": self.use_modifiers
        }

        submodels = (
            build_submodel_from_object(obj, config) for obj in objects
        )
        # TODO: Includes export

        with open(self.filepath, "w") as outfile:
            t3d.dump(outfile, submodels)

        return {'FINISHED'}


class T3DSubmodelProperties(bpy.types.PropertyGroup):
    anim: EnumProperty(
        name='Anim',
        default='false',
        items=[
            ('ik22', 'ik22', ''),
            ('ik21', 'ik21', ''),
            ('ik11', 'ik11', ''),
            ('ik', 'ik', ''),
            ('hours24_jump', 'hours24_jump', ''),
            ('hours24', 'hours24', ''),
            ('hours_jump', 'hours_jump', ''),
            ('hours', 'hours', ''),
            ('minutes_jump', 'minutes_jump', ''),
            ('minutes', 'minutes', ''),
            ('seconds_jump', 'seconds_jump', ''),
            ('seconds', 'seconds', ''),
            ('digital', 'digital', ''),
            ('digiclk', 'digiclk', ''),
            ('billboard', 'billboard', ''),
            ('wind', 'wind', ''),
            ('sky', 'sky', ''),
            ('true', 'true', ''),
            ('false', 'false', '')
        ]
    )

    max_distance: FloatProperty(
        name='Max Distance',
        min=-1,
        default=-1,
        step=0.1,
        unit='LENGTH'
    )

    min_distance: FloatProperty(
        name='Min Distance',
        min=0,
        step=0.1,
        unit='LENGTH'
    )

    selfillum: FloatProperty(
        name='SelfIllum',
        default=0,
        min=-1.25,
        max=1.25,
        step=0.01
    )

    ambient_color: FloatVectorProperty(
        name='Ambient',
        subtype='COLOR',
        default=(255, 255, 255),
        min=0,
        max=255,
    )

    diffuse_color: FloatVectorProperty(
        name='Diffuse',
        subtype='COLOR',
        default=(255, 255, 255),
        min=0,
        max=255,
    )

    specular_color: FloatVectorProperty(
        name='Specular',
        subtype='COLOR',
        default=(255, 255, 255),
        min=0,
        max=255,
    )

    wire: BoolProperty(
        name='Wire',
        default=False,
    )

    wire_size: FloatProperty(
        name="Size",
        min=0,
        default=1
    )

    opacity: FloatProperty(
        name='Opacity',
        min=0,
        max=1,
        default=1
    )

    replacableskin_id: EnumProperty(
        name='Skin',
        default='None',
        items=[
            ('None', 'None', ''),
            ('-1', '-1', ''),
            ('-2', '-2', ''),
            ('-3', '-3', ''),
            ('-4', '-4', '')]
    )

    use_normals: BoolProperty(
        name="Use explicit normals",
        default=False
    )

    use_near_atten: BoolProperty(
        name='UseNearAtten',
        default=False,
    )

    near_atten_start: FloatProperty(
        name='NearAttenStart',
        default=40,
        min=0,
        unit='LENGTH'
    )

    near_atten_end: FloatProperty(
        name='NearAttenEnd',
        default=0,
        min=0,
        unit='LENGTH'
    )

    far_atten_decay_type: IntProperty(
        name='FarAttenDecayType',
        default=1,
        min=0,
        max=2
    )


class T3DSubmodelPropertiesPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_t3d"
    bl_label = "T3D Submodel Properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    def draw(self, context):
        self.obj = context.object
        
        self.obj_is_mesh = (self.obj.type == 'MESH')
        self.obj_is_spot = (self.obj.type == 'LIGHT' and self.obj.data.type == 'SPOT')
        self.obj_is_stars = (self.obj.type == 'EMPTY')

        obj_is_exportable = (self.obj_is_mesh or self.obj_is_spot or self.obj_is_stars)
        if obj_is_exportable:
            self.draw_panel()
        else:
            self.layout.label("This object is not supported by T3D format.")

    def draw_panel(self):
        name_r = self.layout.row()
        name_r.prop(self.obj, "name")

        parent_r = self.layout.row()
        parent_r.prop(self.obj, "parent")

        anim_r = self.layout.row()
        anim_r.prop(self.obj.t3d_properties, "anim")

        selfillum_r = self.layout.row()
        selfillum_r.prop(self.obj.t3d_properties, "selfillum")

        diffuse_r = self.layout.row()
        diffuse_r.prop(self.obj.t3d_properties, "diffuse_color")

        if (self.obj_is_mesh):
            ambient_r = self.layout.row()
            ambient_r.prop(self.obj.t3d_properties, "ambient_color")

            specular_r = self.layout.row()
            specular_r.prop(self.obj.t3d_properties, "specular_color")

            wire_b = self.layout.box()

            wire_r = wire_b.row()
            wire_r.prop(self.obj.t3d_properties, "wire")

            wiresize_r = wire_b.row()
            wiresize_r.prop(self.obj.t3d_properties, "wire_size")

            opacity_r = self.layout.row()
            opacity_r.prop(self.obj.t3d_properties, "opacity")

            map_b = self.layout.box()
            replacableskin_r = map_b.row()
            replacableskin_r.prop(self.obj.t3d_properties, "replacableskin_id")

            use_normals_r = self.layout.row()
            use_normals_r.prop(self.obj.t3d_properties, "use_normals")

        elif (self.obj_is_spot):
            near_atten_box = self.layout.box()

            use_near_atten_r = near_atten_box.row()
            use_near_atten_r.prop(self.obj.t3d_properties, "use_near_atten")

            near_atten_start_r = near_atten_box.row()
            near_atten_start_r.prop(self.obj.t3d_properties, "near_atten_start")

            near_atten_end_r = near_atten_box.row()
            near_atten_end_r.prop(self.obj.t3d_properties, "near_atten_end")

            far_atten_decay_type_r = self.layout.row()
            far_atten_decay_type_r.prop(self.obj.t3d_properties, "far_atten_decay_type")

            far_decay_radius_r = self.layout.row()
            far_decay_radius_r.prop(self.obj.data, "distance", text="FarDecayRadius")

        maxdistance_r = self.layout.row()
        maxdistance_r.prop(self.obj.t3d_properties, "max_distance")

        mindistance_r = self.layout.row()
        mindistance_r.prop(self.obj.t3d_properties, "min_distance")

            

