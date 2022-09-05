from .common import draw_node_ui

def draw(context, layout):
    props = context.object.eu07_scn_lines

    row = layout.row()
    row.operator("wm.url_open", text="Documentation", icon='QUESTION').url = "https://wiki.eu07.pl/index.php/Obiekt_node::lines"

    draw_node_ui(layout, props)

    row = layout.row()
    row.prop(props, "thickness")

    row = layout.row()
    row.prop(props, "color")


