from scn.core.entity.track.validate import is_track_junction

from .common import draw_node_ui

def draw(context, layout):
    props = context.object.eu07_scn_traction

    row = layout.row()
    row.operator("wm.url_open", text="Documentation", icon='QUESTION').url = "https://wiki.eu07.pl/index.php/Obiekt_node::traction"

    draw_node_ui(layout, props)

    row = layout.row()
    row.prop(props, "power_supply_name")

    row = layout.row()
    row.prop(props, "nominal_voltage")

    row = layout.row()
    row.prop(props, "max_current")

    row = layout.row()
    row.prop(props, "resistivity")

    row = layout.row()
    row.prop(props, "material")

    row = layout.row()
    row.prop(props, "wire_thickness")

    row = layout.row()
    row.prop(props, "damage_flag")

    row = layout.row()
    row.prop(props, "p1")

    row = layout.row()
    row.prop(props, "p2")

    row = layout.row()
    row.prop(props, "p3")

    row = layout.row()
    row.prop(props, "p4")

    row = layout.row()
    row.prop(props, "min_height")

    row = layout.row()
    row.prop(props, "segment_length")

    row = layout.row()
    row.prop(props, "wires")

    row = layout.row()
    row.prop(props, "wires_offset")

    row = layout.row()
    row.prop(props, "visible")

    row = layout.row()
    row.prop(props, "parallel")





