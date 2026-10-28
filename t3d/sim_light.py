"""
FreeSpotLight submodels the way the simulator lights the scene with them (rendering/common/locallights.cpp and
shaders/*/light_common.glsl of the simulator).

The simulator: a spot light along -z of the submodel, in the colour Diffuse^2.2 * gfx.lights.freespot.intensity *
HotspotPower / 100. A surface of albedo A gets A * colour * cos / d^2 from it, which also goes smoothly to nothing at the
range of the light, sqrt(max(colour) / 0.01) but no more than 60 m, and no closer than 0.1 m. It fades from the falloff
cone to the hotspot cone with a smoothstep of the cosines. A FalloffAngle of 360 makes it a point light.

Blender (Cycles and EEVEE alike): a surface of albedo A gets A * color * energy / (4 pi^2) * cos / d^2 from a point or a
spot light, and a spot light fades from cos(spot_size / 2) to cos(spot_size / 2) + (1 - cos(spot_size / 2)) * spot_blend
with a smoothstep. So the colour of the light is Diffuse^2.2, its energy 4 pi^2 * gfx.lights.freespot.intensity *
HotspotPower / 100, and the blend the share of the hotspot cone in the cosines. The fade at the range is made by the node
tree of the light (both engines take it), and the influence of the light in EEVEE ends at the range.

The optional parameters of the light take the rest of a light of Blender:
- Radius: the radius of the light, which shines from the surface of its sphere: the same as a point beyond it while the
  sphere is above the horizon of a surface, and 1 / r^2 within it; the simulator does the same. Its shadows aren't cast by
  what is within the sphere (the glass of the lamp the middle of the light is in);
- SoftFalloff: the Soft Falloff of Blender, with which the light falls off as 1 / (d^2 + r^2);
- CastShadows: the Shadow of the light;
- ShadeSelf: whether the model of the light casts its shadows. Blender shadows a light by everything which casts shadows,
  unless its Shadow Linking leaves an object out; an imported model without ShadeSelf gets the linking which leaves its
  objects out (a collection made for the light), as the simulator doesn't shadow the light by them.
The colour of the Temperature, the Exposure and the Normalize of the light go to the Diffuse and the HotspotPower of the
model, which the colour brighter than white (of a temperature) goes to as well.
"""

import math

import bpy

GAMMA = 2.2
# gfx.lights.freespot.intensity of the simulator
FREESPOT_INTENSITY_DEFAULT = 10.0
# a light ends where its contribution falls under this, and reaches no farther than LIGHT_RANGE_MAX metres
LIGHT_THRESHOLD = 0.01
LIGHT_RANGE_MAX = 60.0
# the square of the distance below which a point light gets no brighter
LIGHT_MIN_DISTANCE2 = 0.01
# energy of a blender light which gives a surface as much light as a light of the simulator of colour 1
WATTS_PER_UNIT = 4.0 * math.pi ** 2

# cones of the model wider than a half of the space, which a spot light of blender cannot have
COS_FALLOFF_KEY = "eu07_cos_falloff"
COS_HOTSPOT_KEY = "eu07_cos_hotspot"

NODE_PREFIX = "EU07 "
# the collection of the Shadow Linking made for a light whose model doesn't shadow it
BLOCKERS_PREFIX = "EU07 ShadeSelf "
# the types of objects which go to the model as geometry
GEOMETRY_TYPES = ('MESH', 'CURVE', 'SURFACE', 'META', 'FONT')


def freespot_intensity(scene=None):
    if scene is None:
        scene = getattr(bpy.context, "scene", None)
    if scene is None:
        return FREESPOT_INTENSITY_DEFAULT
    return scene.eu07_freespot_intensity


def power_to_energy(power, scene=None):
    """ HotspotPower (percent) to the energy of the blender light """
    return power * 0.01 * freespot_intensity(scene) * WATTS_PER_UNIT


def energy_to_power(energy, scene=None):
    """ Energy of the blender light to HotspotPower (percent) """
    return energy / (0.01 * freespot_intensity(scene) * WATTS_PER_UNIT)


def diffuse_to_color(diffuse):
    """ Diffuse of the model, 0-255, to the (linear) colour of the blender light """
    return [max(value / 255, 0.0) ** GAMMA for value in diffuse]


def color_to_diffuse(color):
    """ Colour of the blender light to the diffuse of the model, 0-255 """
    return [max(value, 0.0) ** (1 / GAMMA) * 255 for value in color]


def energy_factor(light):
    """ What Blender multiplies the energy of the light by: 2^Exposure, and without Normalize the area of the sphere of the
    light (4 for a point), whose square metre the energy is given for then """
    factor = 2.0 ** light.exposure
    if not light.normalize:
        radius = light.shadow_soft_size
        factor *= 4.0 * math.pi * radius * radius if radius > 0.0 else 4.0
    return factor


def light_color(light):
    """ The colour Blender lights with: the Color, by the colour of the Temperature when it's used """
    if not light.use_temperature:
        return [max(value, 0.0) for value in light.color]
    return [max(value, 0.0) * temperature for value, temperature in zip(light.color, light.temperature_color)]


def model_values(light):
    """ Diffuse (0-255) and HotspotPower (percent) of the model for the light as Blender lights with it: its colour with the
    temperature, its energy with the exposure and the normalization. A colour brighter than white goes to the power """
    color = light_color(light)
    energy = light.energy * energy_factor(light)
    peak = max(color)
    if peak > 1.0:
        color = [value / peak for value in color]
        energy *= peak
    return color_to_diffuse(color), energy_to_power(energy)


def angle_to_cos(angle):
    """ FalloffAngle or HotspotAngle of the model: a cosine, or degrees of the whole cone above 1 """
    return math.cos(math.radians(0.5 * angle)) if angle > 1 else angle


def is_point_cone(cos_falloff):
    """ A cone of the whole sphere (FalloffAngle 360), which makes a point light """
    return cos_falloff <= -0.9999


def simulator_cones(cos_falloff, cos_hotspot):
    """ Cosines of the cone the light fades out at and of the one it is full within, as the simulator takes them:
    the glare goes from no brightness at the falloff angle to full at the hotspot angle, which some models have the
    wrong way round """
    cos_outer = min(max(cos_falloff, -1.0), 0.999)
    cos_inner = min(max(max(cos_hotspot, cos_outer + 0.05), cos_outer + 0.001), 1.0)
    return cos_outer, cos_inner


def is_simulator_light(light):
    return light is not None and light.type in ('SPOT', 'POINT') and light.eu07_simulator_light


def set_cones(light, cos_falloff, cos_hotspot):
    """ Sets the cone of the spot light to the one the simulator shows the cones of the model with """
    if light.type != 'SPOT':
        return
    cos_outer, cos_inner = simulator_cones(cos_falloff, cos_hotspot)
    if cos_outer < 0.0:
        # blender has no spot light wider than a half of the space: it shows the half, and the cones of the model are
        # kept for the export while the cone stays so
        light[COS_FALLOFF_KEY] = cos_outer
        light[COS_HOTSPOT_KEY] = cos_inner
    else:
        for key in (COS_FALLOFF_KEY, COS_HOTSPOT_KEY):
            if key in light:
                del light[key]
    cos_outer = max(cos_outer, 0.0)
    light.spot_size = 2.0 * math.acos(cos_outer)
    light.spot_blend = min(max((cos_inner - cos_outer) / (1.0 - cos_outer), 0.0), 1.0)


def blender_cones(light):
    """ Cosines of the falloff and the hotspot cones of the light: the whole sphere for a point light """
    if light.type != 'SPOT':
        return -1.0, -1.0
    cos_outer = math.cos(0.5 * light.spot_size)
    cos_inner = cos_outer + (1.0 - cos_outer) * light.spot_blend
    return cos_outer, cos_inner


def model_cones(light):
    """ Cosines of the falloff and the hotspot cones to write to the model """
    if light.type == 'SPOT' and COS_FALLOFF_KEY in light and light.spot_size >= math.pi - 1e-4:
        return light[COS_FALLOFF_KEY], light.get(COS_HOTSPOT_KEY, 0.0)
    return blender_cones(light)


def cos_to_angle(cos):
    """ Cosine of a half of a cone to the angle of the whole cone, radians """
    return 2.0 * math.acos(min(max(cos, -1.0), 1.0))


def light_range(light):
    """ Distance the simulator takes the light to, metres """
    brightness = max(light_color(light)) * light.energy * energy_factor(light) / WATTS_PER_UNIT
    return min(math.sqrt(max(brightness, 0.0) / LIGHT_THRESHOLD), LIGHT_RANGE_MAX)


def near_factor(light):
    """ What the square of the distance is multiplied by for the share of the light the node tree lets through near the
    light: a point gets no brighter than at 0.1 m, a light with a radius is as bright as its sphere gives it """
    return 1.0 / LIGHT_MIN_DISTANCE2 if light.shadow_soft_size <= 0.0 else 1e12


def _set_value(socket, value):
    if abs(socket.default_value - value) > 1e-6 * max(1.0, abs(value)):
        socket.default_value = value


def update_range(light):
    """ The influence of the light in EEVEE ends at its range, and its node tree fades it out there (and keeps a point no
    brighter than at 0.1 m). They follow the colour, the energy, the exposure, the temperature and the radius of the light,
    which the depsgraph handler keeps them up to date with: a driver of the light reading the light itself would be a
    dependency cycle """
    reach = light_range(light)
    if light.use_custom_distance:
        cutoff = max(reach, 0.01)
        if abs(light.cutoff_distance - cutoff) > 1e-4:
            light.cutoff_distance = cutoff
    tree = light.node_tree
    if tree is None:
        return
    reach_node = tree.nodes.get(NODE_PREFIX + "Range")
    if reach_node is not None:
        if tree.animation_data:
            # the driver lights made before had it follow
            for fcurve in [fc for fc in tree.animation_data.drivers if f'nodes["{reach_node.name}"]' in fc.data_path]:
                tree.animation_data.drivers.remove(fcurve)
        _set_value(reach_node.outputs[0], reach)
    near_node = tree.nodes.get(NODE_PREFIX + "Near")
    if near_node is not None:
        _set_value(near_node.inputs[1], near_factor(light))


@bpy.app.handlers.persistent
def on_depsgraph_update(scene, depsgraph):
    for update in depsgraph.updates:
        if isinstance(update.id, bpy.types.Light):
            light = update.id.original
            if is_simulator_light(light):
                update_range(light)


def _math(nodes, links, name, operation, location, a=None, b=None, clamp=False):
    node = nodes.new("ShaderNodeMath")
    node.name = node.label = NODE_PREFIX + name
    node.operation = operation
    node.use_clamp = clamp
    node.location = location
    for index, value in enumerate((a, b)):
        if value is None:
            continue
        if isinstance(value, (int, float)):
            node.inputs[index].default_value = value
        else:
            links.new(value, node.inputs[index])
    return node


def setup_range(light):
    """ Makes the light fade to nothing at its range, as the simulator does, by its node tree, which update_range() keeps
    up to date with the light """
    light.use_custom_distance = True

    tree = light.node_tree
    if tree is None:
        light.use_nodes = True
        tree = light.node_tree
    nodes, links = tree.nodes, tree.links

    for node in [node for node in nodes if node.name.startswith(NODE_PREFIX)]:
        if tree.animation_data:
            for fcurve in [fc for fc in tree.animation_data.drivers if f'nodes["{node.name}"]' in fc.data_path]:
                tree.animation_data.drivers.remove(fcurve)
        nodes.remove(node)

    output = next((node for node in nodes if node.type == 'OUTPUT_LIGHT' and node.is_active_output), None)
    if output is None:
        output = next((node for node in nodes if node.type == 'OUTPUT_LIGHT'), None) or nodes.new("ShaderNodeOutputLight")
    if output.inputs["Surface"].links:
        emission = output.inputs["Surface"].links[0].from_node
    else:
        emission = nodes.new("ShaderNodeEmission")
        emission.location = (output.location.x - 200, output.location.y)
        links.new(emission.outputs[0], output.inputs["Surface"])
    if emission.type != 'EMISSION':
        # a node tree of its own: left as it is
        update_range(light)
        return

    x, y = emission.location.x - 1200, emission.location.y - 150
    falloff = nodes.new("ShaderNodeLightFalloff")
    falloff.name = falloff.label = NODE_PREFIX + "Distance"
    falloff.location = (x, y)
    falloff.inputs["Strength"].default_value = 1.0
    falloff.inputs["Smooth"].default_value = 0.0
    # the linear output is the strength times the distance
    distance = falloff.outputs["Linear"]

    reach = nodes.new("ShaderNodeValue")
    reach.name = reach.label = NODE_PREFIX + "Range"
    reach.location = (x, y - 200)
    reach.outputs[0].default_value = light_range(light)

    # (1 - (d / range)^4)^2
    ratio = _math(nodes, links, "Distance / Range", 'DIVIDE', (x + 200, y), distance, reach.outputs[0])
    power4 = _math(nodes, links, "^4", 'POWER', (x + 400, y), ratio.outputs[0], 4.0)
    edge = _math(nodes, links, "1 - ^4", 'SUBTRACT', (x + 600, y), 1.0, power4.outputs[0], clamp=True)
    window = _math(nodes, links, "Edge^2", 'MULTIPLY', (x + 800, y), edge.outputs[0], edge.outputs[0])
    # a point no brighter than at 0.1 m
    square = _math(nodes, links, "Distance^2", 'MULTIPLY', (x + 200, y - 200), distance, distance)
    near = _math(nodes, links, "Near", 'MULTIPLY', (x + 400, y - 200), square.outputs[0], near_factor(light), clamp=True)
    strength = _math(nodes, links, "Strength", 'MULTIPLY', (x + 1000, y), window.outputs[0], near.outputs[0])
    links.new(strength.outputs[0], emission.inputs["Strength"])
    update_range(light)


def make_simulator_light(light, power=100.0, radius=0.0):
    """ Marks the spot or point light as one in the units of the simulator and sets it up as the simulator shows it """
    light.eu07_simulator_light = True
    # the energy and the colour as they are, see model_values()
    light.exposure = 0.0
    light.normalize = True
    light.use_temperature = False
    light.energy = power_to_energy(power)
    # a point, as in the simulator, unless the model gives the light a radius
    light.shadow_soft_size = radius
    light.use_soft_falloff = False
    setup_range(light)


def convert_legacy_light(light):
    """ Turns a spot light made before the simulator units, whose colour and blend went to the model as they were, into
    one in the units, which gives the model the same Diffuse, FalloffAngle and HotspotAngle. A point light (a point of
    stars) becomes a point light of the simulator of the same Diffuse """
    diffuse = [value * 255 for value in light.color]
    light.color = diffuse_to_color(diffuse)
    if light.type == 'SPOT':
        falloff = math.degrees(light.spot_size)
        hotspot = math.degrees(light.spot_size * (1 - light.spot_blend))
        set_cones(light, angle_to_cos(falloff), angle_to_cos(hotspot))
    make_simulator_light(light)


def rescale_simulator_lights(ratio):
    for light in bpy.data.lights:
        if is_simulator_light(light):
            light.energy *= ratio


# ShadeSelf and the Shadow Linking of Blender

def _link_states(collection):
    """ (object or collection, link state) of the members of a collection of the light linking """
    for obj, member in zip(collection.objects, collection.collection_objects):
        yield obj, member.light_linking.link_state
    for child, member in zip(collection.children, collection.collection_children):
        yield child, member.light_linking.link_state


def casts_shadow(light_obj, obj):
    """ Whether the object shadows the light in Blender: it casts shadows, and the Shadow Linking of the light, if any,
    doesn't leave it out """
    if not obj.visible_shadow:
        return False
    blockers = light_obj.light_linking.blocker_collection
    if blockers is None:
        return True
    included = False
    for member, state in _link_states(blockers):
        if state == 'INCLUDE':
            included = True
        if member == obj or (isinstance(member, bpy.types.Collection) and obj.name in member.all_objects):
            return state == 'INCLUDE'
    # objects not in the collection are shadowed by when it includes nothing
    return not included


def shade_self(light_obj, objects):
    """ ShadeSelf of the light: whether any of the objects of its model shadows it in Blender """
    return any(casts_shadow(light_obj, obj) for obj in objects if obj.type in GEOMETRY_TYPES and obj != light_obj)


def set_shade_self(light_obj, objects, value):
    """ Makes the objects of the model of the light shadow it in Blender or not, by a Shadow Linking collection made for
    the light, as the simulator does with ShadeSelf """
    blockers = light_obj.light_linking.blocker_collection
    ours = blockers is not None and blockers.name.startswith(BLOCKERS_PREFIX)
    if value:
        if ours:
            light_obj.light_linking.blocker_collection = None
            if blockers.users == 0:
                bpy.data.collections.remove(blockers)
        return
    if blockers is None:
        blockers = bpy.data.collections.new(BLOCKERS_PREFIX + light_obj.name)
        light_obj.light_linking.blocker_collection = blockers
    elif not ours:
        # a linking of the user's own: left as it is
        return
    for obj in objects:
        if obj.type in GEOMETRY_TYPES and obj != light_obj and obj.name not in blockers.objects:
            blockers.objects.link(obj)
    for obj, member in zip(blockers.objects, blockers.collection_objects):
        member.light_linking.link_state = 'EXCLUDE'
