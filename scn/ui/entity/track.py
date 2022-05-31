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
    row.operator("eu07.import_material", text="", icon="PLUS")

    row = layout.row()
    row.prop(props, "map1_length")

    row = layout.row()
    row.prop(props, "map2")
    row.operator("eu07.import_material", text="", icon="PLUS")

    row = layout.row()
    row.prop(props, "geometry_params", text="Ballast geometry")

    row = layout.row()
    row.prop(props, "p1", text="P1")

    row = layout.row()
    row.prop(props, "cv1", text="CV1")

    row = layout.row()
    row.prop(props, "cv2", text="CV2")

    row = layout.row()
    row.prop(props, "p2", text="P2")

    row = layout.row()
    row.prop(props, "radius1", text="Radius 1")

    if is_track_junction(context.object):
        row = layout.row()
        row.prop(props, "p3", text="P3")

        row = layout.row()
        row.prop(props, "cv3", text="CV3")

        row = layout.row()
        row.prop(props, "cv4", text="CV4")

        row = layout.row()
        row.prop(props, "p4", text="P4")

        row = layout.row()
        row.prop(props, "radius2", text="Radius 2")

    row = layout.row()
    row.prop(props, "velocity", text="Velocity")

    row = layout.row()
    row.prop(props, "event0_name", text="Event 0")

    row = layout.row()
    row.prop(props, "event1_name", text="Event 1")

    row = layout.row()
    row.prop(props, "event2_name", text="Event 2")

    row = layout.row()
    row.prop(props, "eventall0_name", text="EventAll 0")

    row = layout.row()
    row.prop(props, "eventall1_name", text="EventAll 1")

    row = layout.row()
    row.prop(props, "eventall2_name", text="EventAll 2")

    row = layout.row()
    row.prop(props, "event0_name", text="Event 0")

    row = layout.row()
    row.prop(props, "event1_name", text="Event 1")

    row = layout.row()
    row.prop(props, "isolated_name", text="Isolated")

    row = layout.row()
    row.prop(props, "overhead", text="Overhead")

    row = layout.row()
    row.prop(props, "angle1", text="Angle 1")

    row = layout.row()
    row.prop(props, "angle2", text="Angle 2")

    row = layout.row()
    row.prop(props, "fouling1", text="Fouling 1")

    row = layout.row()
    row.prop(props, "fouling2", text="Fouling 2")

    row = layout.row()
    row.prop(props, "railprofile", text="Rail Profile")

    row = layout.row()
    row.prop(props, "friction_memcell", text="Friction Memcell")


