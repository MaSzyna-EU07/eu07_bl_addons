import os
import bpy.utils.previews

_ICON_PATHS = {
    "sz_icon": "sz_icon.png"
}

_pcoll = bpy.utils.previews.new()


def get_icon_id(name):
    icon = _pcoll.get(name)
    return icon.icon_id if icon else 0


def get_icons():
    for name, path in _ICON_PATHS.items():
        try:
            preview = _pcoll.load(name, os.path.join(os.path.dirname(__file__), path), 'IMAGE')
        except KeyError:
            pass

def clear_icons():
    bpy.utils.previews.remove(_pcoll)


def register():
    get_icons()


def unregister():
    clear_icons()
