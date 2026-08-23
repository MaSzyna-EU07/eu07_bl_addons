import bpy
from bpy.props import EnumProperty, FloatProperty, IntProperty, FloatVectorProperty, BoolProperty, StringProperty

import icons


def has_action(self):
    anim_data = self.id_data.animation_data
    return anim_data is not None and anim_data.action is not None

def is_mesh(self):
    return self.id_data.type in ('MESH', 'CURVE', 'SURFACE', 'META', 'FONT')

def is_freespotlight(self):
    return self.id_data.type == 'LIGHT' and self.id_data.data.type == 'SPOT'

def is_stars(self):
    if self.id_data.type == 'EMPTY':
        for child in self.id_data.children:
            if child.t3d_properties.is_star_point:
                return True

    return False

def is_star_point(self):
    return self.id_data.type == 'LIGHT' and self.id_data.data.type == 'POINT'

def get_true_selfillum(self):
    if self.is_freespotlight or self.is_stars:
        return self.selfillum_light
    else:
        return self.selfillum


class T3DSubmodelProperties(bpy.types.PropertyGroup):
    has_action: BoolProperty(
        get=has_action
    )

    is_mesh: BoolProperty(
        get=is_mesh
    )

    is_freespotlight: BoolProperty(
        get=is_freespotlight
    )

    is_stars: BoolProperty(
        get=is_stars
    )

    is_star_point: BoolProperty(
        get=is_star_point
    )

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
            ('false', 'false', ''),
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
    selfillum_light: FloatProperty(
        name='SelfIllum',
        default=2,
        min=-1,
        max=2,
        step=0.01
    )
    true_selfillum: FloatProperty(
        get=get_true_selfillum
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
        name="Wire Size",
        min=0,
        default=1
    )
    opacity: FloatProperty(
        name='Opacity',
        min=0,
        max=1,
        default=1
    )
    opacity_source: EnumProperty(
        name='Opacity Source',
        description="Where the opacity value used on export comes from",
        default='OBJECT',
        items=[
            ('OBJECT', 'Object', 'Opacity is taken from this object'),
            ('MATERIAL', 'Material', 'Opacity comes from the imported material'),
        ]
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
    bl_label = "T3D Properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    def draw_header(self, context):
        icons.get_icons()
        self.layout.label(text="", icon_value=icons.get_icon_id("sz_icon"))

    def draw(self, context):
        self.obj = context.object

        if self.obj.t3d_properties.is_star_point:
            self.layout.prop(self.obj.data, "color", text="Point Color")
            return

        np_b = self.layout.box()

        name_r = np_b.row()
        name_r.prop(self.obj, "name")

        parent_r = np_b.row()
        parent_r.prop(self.obj, "parent")

        anim_b = self.layout.box()
        anim_r = anim_b.row()
        anim_r.prop(self.obj.t3d_properties, "anim")

        if self.obj.t3d_properties.has_action:
            anim_r.enabled = False
            anim_b.row().label(text="Anim: true (object has action)", icon='ANIM_DATA')
        else:
            anim_r.enabled = True

        selfillum_b = self.layout.box()
        selfillum_r = selfillum_b.row()
        selfillum_r.prop(
            self.obj.t3d_properties,
            "selfillum_light" if self.obj.t3d_properties.is_freespotlight
                                or self.obj.t3d_properties.is_stars
            else "selfillum"
        )

        if self.obj.t3d_properties.is_freespotlight:
            colors_b = self.layout.box()
            diffuse_r = colors_b.row()
            diffuse_r.prop(self.obj.data, "color", text="Diffuse")

            near_atten_b = self.layout.box()

            use_near_atten_r = near_atten_b.row()
            use_near_atten_r.prop(self.obj.t3d_properties, "use_near_atten")

            near_atten_start_r = near_atten_b.row()
            near_atten_start_r.prop(self.obj.t3d_properties, "near_atten_start")

            near_atten_end_r = near_atten_b.row()
            near_atten_end_r.prop(self.obj.t3d_properties, "near_atten_end")

            far_atten_b = self.layout.box()
            far_atten_decay_type_r = far_atten_b.row()
            far_atten_decay_type_r.prop(self.obj.t3d_properties, "far_atten_decay_type")

            far_decay_radius_r = far_atten_b.row()
            far_decay_radius_r.prop(self.obj.t3d_properties, "far_decay_radius")

        elif self.obj.t3d_properties.is_stars:
            colors_b = self.layout.box()
            diffuse_r = colors_b.row()
            diffuse_r.prop(self.obj.t3d_properties, "diffuse_color")

        else:
            colors_b = self.layout.box()
            diffuse_r = colors_b.row()
            diffuse_r.prop(self.obj.t3d_properties, "diffuse_color")

            ambient_r = colors_b.row()
            ambient_r.prop(self.obj.t3d_properties, "ambient_color")

            specular_r = colors_b.row()
            specular_r.prop(self.obj.t3d_properties, "specular_color")

            #wire_b = self.layout.box()

            #wire_r = wire_b.row()
            #wire_r.prop(self.obj.t3d_properties, "wire")

            #wiresize_r = wire_b.row()
            #wiresize_r.prop(self.obj.t3d_properties, "wire_size")

            om_b = self.layout.box()

            replacableskin_r = om_b.row()
            replacableskin_r.prop(self.obj.t3d_properties, "replacableskin_id")

            opacity_row = om_b.row()
            opacity_row.prop(self.obj.t3d_properties, "opacity", text="Opacity")

        dist_b = self.layout.box()

        maxdistance_r = dist_b.row()
        maxdistance_r.prop(self.obj.t3d_properties, "max_distance")

        mindistance_r = dist_b.row()
        mindistance_r.prop(self.obj.t3d_properties, "min_distance")