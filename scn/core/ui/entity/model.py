from .....scn.core.entity.track.validate import is_track_junction

from .common import draw_node_ui

def draw(context, layout):
    props = context.object.eu07_scn_model

    row = layout.row()
    row.operator("wm.url_open", text="Documentation", icon='QUESTION').url = "https://wiki.eu07.pl/index.php/Obiekt_node::model"

    draw_node_ui(layout, props)

    row = layout.row()
    row.prop(props, "location")

    row = layout.row()
    row.prop(props, "rotation")

    row = layout.row()
    row.prop(props, "model_path")

    box = layout.box()
    row = box.row()
    row.label(text="Replaceable skins")

    skin_ids = [skin.skin_id for skin in context.object.data.eu07_scn_model_skins]

    if -1 in skin_ids:
        row = box.row()
        row.prop(props, "replacableskin_1")

    if -2 in skin_ids:
        row = box.row()
        row.prop(props, "replacableskin_2")

    if -3 in skin_ids:
        row = box.row()
        row.prop(props, "replacableskin_3")

    if -4 in skin_ids:
        row = box.row()
        row.prop(props, "replacableskin_4")

    row = layout.row()
    row.label(text="lights todo")

    row = layout.row()
    row.label(text="lightcolors todo")

    row = layout.row()
    row.prop(props, "notransition")

