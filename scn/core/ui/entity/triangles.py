from .....scn.core.entity.track.validate import is_track_junction

from .common import draw_node_ui

def draw(context, layout):
    props = context.object.eu07_scn_triangles

    row = layout.row()
    row.operator("wm.url_open", text="Documentation", icon='QUESTION').url = "https://wiki.eu07.pl/index.php/Obiekt_node::triangles"

    draw_node_ui(layout, props)

