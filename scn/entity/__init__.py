import bpy

from . import camera
from . import track
from . import model
from . import traction


def register():
    camera.register()
    track.register()
    model.register()
    traction.register()

    bpy.types.Object.eu07_scn_entity_type = bpy.props.EnumProperty(
        name="Entity Type",
        description="Entity Type",
        items=[
            ("none", "none", "Non-scenery object"),
            ("include", "include", "Static object, defined in *.inc file"),
            ("camera", "camera", "Camera"),
            ("node::eventlauncher", "eventlauncher", "Event launcher"),
            ("node::lines", "lines", "Lines"),
            ("node::memcell", "memcell", "Memory cell"),
            ("node::model", "model", "Static model"),
            ("node::sound", "sound", "Sound emitter"),
            ("node::track", "track", "Trajectory"),
            ("node::traction", "traction", "Catenary wires"),
            ("node::tractionpowersource", "tractionpowersource", "Power source for overhead electric lines"),
            ("node::triangles", "triangles", "Geometry (e.g. terrain)"),
        ],
        default="none",
    )


def unregister():
    camera.unregister()
    track.unregister()
    model.unregister()
    traction.unregister()


