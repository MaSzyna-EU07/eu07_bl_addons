def is_valid_track(obj):
    return (
            is_curve(obj) and
            len(obj.data.splines) == 1 and
            len(obj.data.splines[0].bezier_points) == 2
    )


def is_valid_junction(obj):
    return (
            is_curve(obj) and
            len(obj.data.splines) == 2 and
            len(obj.data.splines[0].bezier_points) == 2 and
            len(obj.data.splines[1].bezier_points) == 2
    )


def is_curve(obj):
    return obj and obj.type == 'CURVE'


def is_track_junction(obj):
    return obj.eu07_track.type in "switch cross tributary"