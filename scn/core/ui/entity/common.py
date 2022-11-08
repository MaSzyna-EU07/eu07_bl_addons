def draw_node_ui(layout, props):
    layout.row().prop(props, "filename")
    layout.row().prop(props, "max_distance")
    layout.row().prop(props, "min_distance")