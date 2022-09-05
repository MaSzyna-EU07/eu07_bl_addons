# NOTE: Main method is at the bottom

def _draw_placeholder(context, layout, props):
    row = layout.row()
    row.prop(props, "params_text")


def _draw_tree(context, layout, props):
    row = layout.row()
    row.prop(props, "skin")

    row = layout.row()
    row.prop(props, "location")

    row = layout.row()
    row.prop(props, "rotation")

    row = layout.row()
    row.prop(props, "height")

    row = layout.row()
    row.prop(props, "span")


_subdraws = {
    "placeholder": _draw_placeholder,
    "tree": _draw_tree,
}

def draw(context, layout):
    props = context.object.eu07_scn_staticinc

    row = layout.row()
    row.prop(props, "subtype")

    row = layout.row()
    row.prop(props, "path")

    subdraw = _subdraws.get(props.subtype)
    if subdraw:
        subdraw(context, layout, props.subprops)




