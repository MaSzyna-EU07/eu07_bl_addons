from scn.geometry.track import create_track_geometry_manager

def setup_track(obj):
    mngr = create_track_geometry_manager(obj)
    container = mngr.get_container_from(obj)
    if not container:
        geometry = mngr.get(obj)
        mngr.set(obj, geometry)

    