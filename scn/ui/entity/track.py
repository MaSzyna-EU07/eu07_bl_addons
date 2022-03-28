def draw(context, layout):
    props = context.object.eu07_track

    row = layout.row()
    row.prop(props, "type")

    row = layout.row()
    row.prop(props, "length")

    row = layout.row()
    row.prop(props, "width")

    row = layout.row()
    row.prop(props, "friction")

    row = layout.row()
    row.prop(props, "sound_distance")

    row = layout.row()
    row.prop(props, "quality_flag")

    row = layout.row()
    row.prop(props, "damage_flag")

    row = layout.row()
    row.prop(props, "environment")

    row = layout.row()
    row.prop(props, "visibility")

    row = layout.row()
    row.prop(props, "map1")

    row = layout.row()
    row.prop(props, "map1_length")

    row = layout.row()
    row.prop(props, "map2")

    row = layout.row()
    row.prop(props, "geometry_params", text="Ballast geometry")

