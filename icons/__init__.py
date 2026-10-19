import os

import bpy.utils.previews

_ICON_PATHS = {
    "sz_icon": "sz_icon.png"
}

_pcoll = None


def get_icon_id(name):
    if _pcoll is None:
        return 0

    icon = _pcoll.get(name)
    return icon.icon_id if icon else 0


def get_icons():
    if _pcoll is None:
        return

    for name, path in _ICON_PATHS.items():
        try:
            _pcoll.load(name, os.path.join(os.path.dirname(__file__), path), 'IMAGE')
        except KeyError:
            pass


def clear_icons():
    global _pcoll

    if _pcoll is not None:
        bpy.utils.previews.remove(_pcoll)
        _pcoll = None


def register():
    global _pcoll

    if _pcoll is None:
        _pcoll = bpy.utils.previews.new()

    get_icons()


def unregister():
    clear_icons()
