import bpy

from .properties import TrackProperties
from .setup import setup_track

classes = (
    TrackProperties,
)

def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.Object.eu07_track = bpy.props.PointerProperty(type=TrackProperties)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)