

def create_entity(type, name):
    creator = entity_factories.get(type)
    if creator:
        return creator(name)


def create_include(name):
    pass


def create_camera(name):
    camera = bpy.data.cameras.new(name)
    return camera


def create_eventlauncher(name):
    pass


def create_lines(name):
    curve = bpy.data.curves.new(name, type='CURVE')
    spline = curve.splines.new('BEZIER')
    obj = bpy.data.objects.new(name, curve)

    return obj


def create_memcell(name):
    pass


def create_model(name):
    pass


def create_sound(name):
    pass


def create_track_2points(name):
    return create_track_generic(name)


def create_track_4points(name):
    return create_track_generic(name, is_junction=True)


def create_track_generic(name, is_junction=False):
    curve = bpy.data.curves.new(name, type='CURVE')
    num_splines = 2 if is_junction else 1
    for i in range(num_splines):
        curve.splines.new('BEZIER')
    obj = bpy.data.objects.new(name, curve)

    return obj


def create_traction(name):
    curve = bpy.data.curves.new(name, type='CURVE')
    spline1 = curve.splines.new('BEZIER')
    spline2 = curve.splines.new('BEZIER')
    obj = bpy.data.objects.new(name, curve)

    return obj


def create_tractionpowersource(name):
    pass


def create_triangles(name):
    mesh = bpy.data.meshes.new()


entity_factories = {
    "include": create_include,
    "camera": create_camera,
    "node:eventlauncher": create_eventlauncher,
    "node:lines": create_lines,
    "node:memcell": create_memcell,
    "node:model": create_model,
    "node:sound": create_sound,
    "node:track:normal": create_track_2points,
    "node:track:road": create_track_2points,
    "node:track:river": create_track_2points,
    "node:track:turn": create_track_2points,
    "node:track:table": create_track_2points,
    "node:track:switch": create_track_4points,
    "node:track:cross": create_track_4points,
    "node:track:tributary": create_track_4points,
    "node:traction": create_traction,
    "node:tractionpowersource": create_tractionpowersource,
    "node:triangles": create_triangles,
}

