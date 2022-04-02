from scn.entity.track.validate import is_track_junction

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

    row = layout.row()
    row.prop(props, "p1", text="P1")

    row = layout.row()
    row.prop(props, "p2", text="P2")

    if is_track_junction(context.object):
        row = layout.row()
        row.prop(props, "p3", text="P3")

        row = layout.row()
        row.prop(props, "p4", text="P4")
