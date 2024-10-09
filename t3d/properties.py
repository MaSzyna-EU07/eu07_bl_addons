import bpy
from bpy.props import EnumProperty, FloatProperty, IntProperty, FloatVectorProperty, BoolProperty

import icons

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
        default=-1,
        min=-1,
        max=2,
        step=0.01
    )
    selfillum_spot: FloatProperty(
        name='SelfIllum',
        default=2,
        min=-1,
        max=2,
        step=0.01
    )
    ambient_color: FloatVectorProperty(
        name='Ambient',
        subtype='COLOR',
        default=(1, 1, 1),
        min=0,
        max=1,
    )
    diffuse_color: FloatVectorProperty(
        name='Diffuse',
        subtype='COLOR',
        default=(1, 1, 1),
        min=0,
        max=1,
    )
    specular_color: FloatVectorProperty(
        name='Specular',
        subtype='COLOR',
        default=(1, 1, 1),
        min=0,
        max=1,
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
        name='Map',
        default='None',
        items=[
            ('None', 'From Material', ''),
            ('-1', 'Skin #1', ''),
            ('-2', 'Skin #2', ''),
            ('-3', 'Skin #3', ''),
            ('-4', 'Skin #4', '')]
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
    far_decay_radius: FloatProperty(
        name='FarDecayRadius',
        default=100,
        min=0,
    )


class T3DSubmodelPropertiesPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_t3d"
    bl_label = "T3D Submodel Properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    def draw_header(self, context):
        icons.get_icons()
        self.layout.label(text="", icon_value=icons.get_icon_id("sz_icon"))

    def draw(self, context):
        self.obj = context.object

        self.obj_is_mesh = (self.obj.type == 'MESH')
        self.obj_is_spot = (self.obj.type == 'LIGHT' and self.obj.data.type == 'SPOT')
        self.obj_is_stars = (self.obj.type == 'EMPTY')

        obj_is_exportable = (self.obj_is_mesh or self.obj_is_spot or self.obj_is_stars)
        if obj_is_exportable:
            self.draw_panel()
        else:
            self.layout.label(text="This object is not supported by T3D format.")

    def draw_panel(self):
        name_r = self.layout.row()
        name_r.prop(self.obj, "name")

        parent_r = self.layout.row()
        parent_r.prop(self.obj, "parent")

        anim_r = self.layout.row()
        anim_r.prop(self.obj.t3d_properties, "anim")

        selfillum_r = self.layout.row()
        selfillum_r.prop(
            self.obj.t3d_properties,
            "selfillum_spot" if self.obj_is_spot else "selfillum"
        )

        if self.obj_is_mesh:
            diffuse_r = self.layout.row()
            diffuse_r.prop(self.obj.t3d_properties, "diffuse_color")

            ambient_r = self.layout.row()
            ambient_r.prop(self.obj.t3d_properties, "ambient_color")

            specular_r = self.layout.row()
            specular_r.prop(self.obj.t3d_properties, "specular_color")

            wire_b = self.layout.box()

            wire_r = wire_b.row()
            wire_r.prop(self.obj.t3d_properties, "wire")

            wiresize_r = wire_b.row()
            wiresize_r.prop(self.obj.t3d_properties, "wire_size")

            opacity_row = self.layout.row()

            opacity_row.prop(self.obj.t3d_properties, "opacity", text="Opacity")

            map_b = self.layout.box()
            replacableskin_r = map_b.row()
            replacableskin_r.prop(self.obj.t3d_properties, "replacableskin_id")

        elif (self.obj_is_spot):
            diffuse_r = self.layout.row()
            diffuse_r.prop(self.obj.data, "color", text="Diffuse")

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
            far_decay_radius_r.prop(self.obj.t3d_properties, "far_decay_radius")

        maxdistance_r = self.layout.row()
        maxdistance_r.prop(self.obj.t3d_properties, "max_distance")

        mindistance_r = self.layout.row()
        mindistance_r.prop(self.obj.t3d_properties, "min_distance")