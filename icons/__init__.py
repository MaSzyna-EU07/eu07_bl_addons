import os
import bpy.utils.previews


class EU07Icon(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name="Icon Name"
    )

    icon_id: bpy.props.IntProperty(
        name="Icon ID",
        default=0
    )


_ICON_PATHS = {
    "sz_icon": "sz_icon.png"
}

_pcoll = bpy.utils.previews.new()


def get_icon_id(name):
    icon = bpy.context.window_manager.eu07_icons.get(name)
    return icon.icon_id if icon else 0


def get_icons():
    eu07_icons = bpy.context.window_manager.eu07_icons

    if len(eu07_icons) == 0:

        for name, path in _ICON_PATHS.items():
            preview = _pcoll.load(name, os.path.join(os.path.dirname(__file__), path), 'IMAGE')

            icon = eu07_icons.add()
            icon.name = name
            icon.icon_id = preview.icon_id

    return eu07_icons


def clear_icons():
    bpy.utils.previews.remove(_pcoll)


classes = (
    EU07Icon,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.WindowManager.eu07_icons = bpy.props.CollectionProperty(
        type=EU07Icon
    )


def unregister():
    del bpy.types.WindowManager.eu07_icons
    clear_icons()

    for cls in classes:
        bpy.utils.unregister_class(cls)
