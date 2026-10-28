import bpy
from bpy.props import EnumProperty, FloatProperty, IntProperty, FloatVectorProperty, BoolProperty, StringProperty

import math

from .. import icons
from . import sim_light


def has_action(self):
    anim_data = self.id_data.animation_data
    return anim_data is not None and anim_data.action is not None

def is_mesh(self):
    return self.id_data.type in ('MESH', 'CURVE', 'SURFACE', 'META', 'FONT')

def is_freespotlight(self):
    # a spot light, or a point light in the units of the simulator (FalloffAngle 360): the other point lights are the points
    # of stars
    obj = self.id_data
    return obj.type == 'LIGHT' and (
        obj.data.type == 'SPOT' or (obj.data.type == 'POINT' and obj.data.eu07_simulator_light)
    )

def is_stars(self):
    if self.id_data.type == 'EMPTY':
        for child in self.id_data.children:
            if child.t3d_properties.is_star_point:
                return True

    return False

def is_star_point(self):
    obj = self.id_data
    return obj.type == 'LIGHT' and obj.data.type == 'POINT' and not obj.data.eu07_simulator_light

def get_true_selfillum(self):
    if self.is_freespotlight or self.is_stars:
        return self.selfillum_light
    else:
        return self.selfillum


# the values of FreeSpotLight in the units of the simulator, held by the blender light itself
def _spot(self):
    return self.id_data.data if self.is_freespotlight else None

def get_hotspot_power(self):
    # with the exposure and the normalization of the light, which go to the model with it
    light = _spot(self)
    return sim_light.energy_to_power(light.energy * sim_light.energy_factor(light)) if light else 100.0

def set_hotspot_power(self, value):
    light = _spot(self)
    if light:
        light.energy = sim_light.power_to_energy(value) / sim_light.energy_factor(light)

def get_light_diffuse(self):
    light = _spot(self)
    return sim_light.color_to_diffuse(light.color) if light else (255.0, 255.0, 255.0)

def set_light_diffuse(self, value):
    light = _spot(self)
    if light:
        light.color = sim_light.diffuse_to_color(value)

def get_hotspot_angle(self):
    light = _spot(self)
    return sim_light.cos_to_angle(sim_light.blender_cones(light)[1]) if light else 0.0

def set_hotspot_angle(self, value):
    light = _spot(self)
    if light and light.type == 'SPOT':
        cos_outer, _ = sim_light.blender_cones(light)
        sim_light.set_cones(light, cos_outer, math.cos(0.5 * value))


def get_freespot_intensity(self):
    return self.get("_eu07_freespot_intensity", sim_light.FREESPOT_INTENSITY_DEFAULT)

def set_freespot_intensity(self, value):
    # the lights keep their HotspotPower
    previous = get_freespot_intensity(self)
    if value > 0 and previous > 0:
        sim_light.rescale_simulator_lights(value / previous)
    self["_eu07_freespot_intensity"] = value


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
    hotspot_power: FloatProperty(
        name='HotspotPower',
        description="Intensity of the light in percent: the energy of the light, in the units of the simulator",
        min=0.001,
        soft_max=1000,
        precision=1,
        get=get_hotspot_power,
        set=set_hotspot_power,
    )
    light_diffuse: FloatVectorProperty(
        name='Diffuse',
        description="Diffuse of the model, 0-255: the colour of the light is Diffuse^2.2, as the simulator takes it",
        size=3,
        min=0,
        max=255,
        precision=1,
        get=get_light_diffuse,
        set=set_light_diffuse,
    )
    hotspot_angle: FloatProperty(
        name='HotspotAngle',
        description="Cone the light is full within: the blend of the spot light",
        subtype='ANGLE',
        min=0,
        max=math.pi,
        get=get_hotspot_angle,
        set=set_hotspot_angle,
    )


class EU07_OT_FreeSpotLightToSimulator(bpy.types.Operator):
    bl_idname = "eu07.freespotlight_to_simulator"
    bl_label = "Use Simulator Light Units"
    bl_description = (
        "Make the selected spot lights light the scene as the simulator does: the colour becomes Diffuse^2.2, the "
        "energy follows HotspotPower and the light fades out at its range. The model gets the same Diffuse, "
        "FalloffAngle and HotspotAngle as before. A point light becomes a point light of the simulator (FalloffAngle "
        "360) instead of a point of stars"
    )
    bl_options = {'REGISTER', 'UNDO'}

    @staticmethod
    def _convertible(obj):
        return obj.type == 'LIGHT' and obj.data.type in ('SPOT', 'POINT') and not obj.data.eu07_simulator_light

    @classmethod
    def poll(cls, context):
        return any(cls._convertible(obj) for obj in context.selected_objects) or (
            context.object is not None and cls._convertible(context.object)
        )

    def execute(self, context):
        objects = set(context.selected_objects)
        if context.object is not None:
            objects.add(context.object)
        lights = {obj.data for obj in objects if self._convertible(obj)}
        for light in lights:
            sim_light.convert_legacy_light(light)
        self.report({'INFO'}, f"{len(lights)} light(s) converted")
        return {'FINISHED'}


def model_objects(context):
    """ The objects which go to the model with the light, for its ShadeSelf: the geometry of the scene """
    return [obj for obj in context.scene.objects if obj.type in sim_light.GEOMETRY_TYPES]


class EU07_OT_FreeSpotLightShadeSelf(bpy.types.Operator):
    bl_idname = "eu07.freespotlight_shade_self"
    bl_label = "ShadeSelf"
    bl_description = (
        "Whether the model shadows the light (ShadeSelf of the simulator). Off, the light gets a Shadow Linking "
        "collection which leaves the geometry of the scene out, so Blender doesn't shadow it by the model either"
    )
    bl_options = {'REGISTER', 'UNDO'}

    shade_self: BoolProperty(name="ShadeSelf")

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.t3d_properties.is_freespotlight

    def execute(self, context):
        sim_light.set_shade_self(context.object, model_objects(context), self.shade_self)
        return {'FINISHED'}


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
            self.layout.operator(EU07_OT_FreeSpotLightToSimulator.bl_idname, text="Make a Point Light of the Simulator")
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
            light = self.obj.data
            colors_b = self.layout.box()
            if sim_light.is_simulator_light(light):
                diffuse_r = colors_b.row()
                diffuse_r.prop(self.obj.t3d_properties, "light_diffuse")
                diffuse_r.prop(light, "color", text="")
                colors_b.row().prop(self.obj.t3d_properties, "hotspot_power")
                colors_b.row().prop(context.scene, "eu07_freespot_intensity")

                diffuse, power = sim_light.model_values(light)
                if (abs(power - self.obj.t3d_properties.hotspot_power) > 0.05
                        or any(abs(a - b) > 0.05 for a, b in zip(diffuse, self.obj.t3d_properties.light_diffuse))):
                    # the colour of the temperature
                    colors_b.row().label(
                        text=f"The model gets Diffuse {diffuse[0]:.0f} {diffuse[1]:.0f} {diffuse[2]:.0f}, "
                             f"HotspotPower {power:.1f}",
                        icon='INFO'
                    )
                if any(abs(getattr(light, factor) - 1.0) > 1e-4
                       for factor in ("diffuse_factor", "specular_factor", "volume_factor")):
                    colors_b.row().label(text="The simulator doesn't take the Influence of the light", icon='ERROR')

                shape_b = self.layout.box()
                shape_b.row().prop(light, "shadow_soft_size", text="Radius")
                soft_r = shape_b.row()
                soft_r.prop(light, "use_soft_falloff", text="SoftFalloff")
                soft_r.enabled = light.shadow_soft_size > 0.0
                shape_b.row().prop(light, "use_shadow", text="CastShadows")
                shade_r = shape_b.row()
                shade_self = sim_light.shade_self(self.obj, model_objects(context))
                shade_r.label(text=f"ShadeSelf: {'true' if shade_self else 'false'}")
                operator = shade_r.operator(
                    EU07_OT_FreeSpotLightShadeSelf.bl_idname, text="Shadow by the Model" if not shade_self else "Not by the Model"
                )
                operator.shade_self = not shade_self
                shade_r.enabled = light.use_shadow

                cones_b = self.layout.box()
                if light.type == 'POINT':
                    cones_b.row().label(text="FalloffAngle, HotspotAngle 360°: a point light")
                else:
                    cones_b.row().prop(light, "spot_size", text="FalloffAngle")
                    cones_b.row().prop(self.obj.t3d_properties, "hotspot_angle")
                cos_outer, cos_inner = sim_light.blender_cones(light)
                if light.type == 'POINT':
                    pass
                elif sim_light.COS_FALLOFF_KEY in light and light.spot_size >= math.pi - 1e-4:
                    cones_b.row().label(
                        text=f"FalloffAngle {math.degrees(sim_light.cos_to_angle(light[sim_light.COS_FALLOFF_KEY])):.1f}° "
                             f"of the model is kept, Blender shows 180°",
                        icon='INFO'
                    )
                elif sim_light.simulator_cones(cos_outer, cos_inner)[1] > cos_inner + 1e-5:
                    effective = sim_light.cos_to_angle(sim_light.simulator_cones(cos_outer, cos_inner)[1])
                    cones_b.row().label(
                        text=f"The simulator narrows HotspotAngle to {math.degrees(effective):.1f}°",
                        icon='ERROR'
                    )
                colors_b.row().label(text=f"Range: {sim_light.light_range(light):.1f} m")
            else:
                diffuse_r = colors_b.row()
                diffuse_r.prop(light, "color", text="Diffuse")
                colors_b.row().label(text="The light is not in the units of the simulator", icon='INFO')
                colors_b.row().operator(EU07_OT_FreeSpotLightToSimulator.bl_idname)

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