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
from eu07_tools.utils import AssetSearcher

from .builders import build_object_from_submodel


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
        # Find the root
        filepath = Path(self.filepath)
        root = Path("")
        for part in filepath.parts:
            if part in "models dynamic":
                break
            root /= part

        root_found = (not root.samefile(filepath))

        if not root_found:
            pass # TODO: get from script prefs
            # then from userprefs

        config = {
            "skins": {
                "replacableskin": self.skin_1,
                "-1": self.skin_1, 
                "-2": self.skin_2, 
                "-3": self.skin_3, 
                "-4": self.skin_4
            },
            "asset_searcher": AssetSearcher(root, filepath.parent),
        }

        # NOTE: Temporary mat discarding
        config["asset_searcher"].textures_finder.remove_extension(".mat")

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
        name='Replacableskin ID',
        default='None',
        items=[
            ('None', 'None', ''),
            ('-1', '-1', ''),
            ('-2', '-2', ''),
            ('-3', '-3', ''),
            ('-4', '-4', '')]
    )

    use_explicit_normals: BoolProperty(
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

        elif (self.obj_is_spot):
            pass

        maxdistance_r = self.layout.row()
        maxdistance_r.prop(self.obj.t3d_properties, "max_distance")

        mindistance_r = self.layout.row()
        mindistance_r.prop(self.obj.t3d_properties, "min_distance")

            

