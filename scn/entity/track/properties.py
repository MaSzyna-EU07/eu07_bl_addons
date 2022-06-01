import bpy

from scn.entity.node import NodeProperties
from . import properties_functions

class TrackProperties(NodeProperties):
    type: bpy.props.EnumProperty(
        name="Trajectory Type",
        description="Type of the trajectory",
        items=[
            ("normal", "normal", "Railroad Track"),
            ("switch", "switch", "Railroad Switch"),
            ("road", "road", "Road"),
            ("cross", "cross", "Road Cross"),
            ("river", "river", "River"),
            ("tributary", "tributary", "River Cross"),
            ("turn", "turn", "Turntable"),
            ("table", "table", "Turntable")
        ],
    )

    length: bpy.props.FloatProperty(
        name="Length",
        description="Length of the trajectory",
        default=0,
        unit="LENGTH",
        get=properties_functions.get_length,
    )

    width: bpy.props.FloatProperty(
        name="Width",
        description="Width of the trajectory",
        default=1.435,
        unit="LENGTH",
        update=properties_functions.update_geometry,
    )

    friction: bpy.props.FloatProperty(
        name="Friction",
        description="Friction factor",
        default=0.15,
    )

    sound_distance: bpy.props.FloatProperty(
        name="Sound distance",
        description="Distance for clatter sound",
        default=-1,
        unit="LENGTH",
    )

    quality_flag: bpy.props.FloatProperty(
        name="Quality flag",
        description="Quality flag",
        default=20,
    )

    damage_flag: bpy.props.FloatProperty(
        name="Damage flag",
        description="Damage flag",
        default=0,
    )

    environment: bpy.props.EnumProperty(
        name="Environment",
        description="Type of the environment",
        items=[
            ("flat", "flat", "Flat terrain"),
            ("mountains", "mountains", "Mountains"),
            ("canyon", "canyon", "Canyon"),
            ("tunnel", "tunnel", "Tunnel"),
            ("bridge", "bridge", "Bridge"),
            ("bank", "bank", "Bank")
        ],
    )

    visibility: bpy.props.EnumProperty(
        name="Visiblity",
        description="Visiblity state",
        items=[
            ("vis", "vis", "Visible"),
            ("unvis", "unvis", "Not visible")
        ],
        update=properties_functions.update_visibility,
    )

    map1: bpy.props.PointerProperty(
        type=bpy.types.Material,
        name="Material #1",
        description="Material name #1",
        update=properties_functions.update_map1,
    )

    map1_length: bpy.props.FloatProperty(
        name="Map #1 Length",
        description="Map #1 repetition distance",
        default=4,
        unit="LENGTH",
        update=properties_functions.update_geometry,
    )

    map2: bpy.props.PointerProperty(
        type=bpy.types.Material,
        name="Material #2",
        description="Material #2",
        update=properties_functions.update_map2,
    )

    geometry_params: bpy.props.FloatVectorProperty(
        size=3,
        default=(0.2, 0.5, 1.3),
        unit="LENGTH",
        update=properties_functions.update_geometry,
    )

    p1: bpy.props.FloatVectorProperty(
        name="Point 1",
        size=3,
        unit="LENGTH",
        set=properties_functions.set_p1,
        get=properties_functions.get_p1,
    )

    p1_roll: bpy.props.FloatProperty(
        name="Point 1 Roll",
        default=0,
    )

    p2: bpy.props.FloatVectorProperty(
        name="Point 2",
        size=3,
        unit="LENGTH",
        set=properties_functions.set_p2,
        get=properties_functions.get_p2,
    )

    p2_roll: bpy.props.FloatProperty(
        name="Point 2 Roll",
        default=0,
    )

    p3: bpy.props.FloatVectorProperty(
        name="Point 3",
        size=3,
        unit="LENGTH",
        set=properties_functions.set_p3,
        get=properties_functions.get_p3,
    )

    p3_roll: bpy.props.FloatProperty(
        name="Point 3 Roll",
        default=0,
    )

    p4: bpy.props.FloatVectorProperty(
        name="Point 4",
        size=3,
        unit="LENGTH",
        set=properties_functions.set_p4,
        get=properties_functions.get_p4,
    )

    p4_roll: bpy.props.FloatProperty(
        name="Point 4 Roll",
        default=0,
    )

    cv1: bpy.props.FloatVectorProperty(
        name="Control Vector 1",
        size=3,
        unit="LENGTH",
        set=properties_functions.set_cv1,
        get=properties_functions.get_cv1,
    )

    cv2: bpy.props.FloatVectorProperty(
        name="Control Vector 2",
        size=3,
        unit="LENGTH",
        set=properties_functions.set_cv2,
        get=properties_functions.get_cv2,
    )

    cv3: bpy.props.FloatVectorProperty(
        name="Control Vector 3",
        size=3,
        unit="LENGTH",
        set=properties_functions.set_cv3,
        get=properties_functions.get_cv3,
    )

    cv4: bpy.props.FloatVectorProperty(
        name="Control Vector 4",
        size=3,
        unit="LENGTH",
        set=properties_functions.set_cv4,
        get=properties_functions.get_cv4,
    )

    radius1: bpy.props.FloatProperty(
        name="Segment 1 radius",
        default=0,
        get=None,
        set=None,
    )

    radius2: bpy.props.FloatProperty(
        name="Segment 2 radius",
        default=0,
        get=None,
        set=None,
    )

    velocity: bpy.props.FloatProperty(
        name="Velocity",
        default=40,
        min=0
    )

    event0_name: bpy.props.StringProperty(
        name="Event 0",
        default=""
    )

    event1_name: bpy.props.StringProperty(
        name="Event 2",
        default=""
    )

    event2_name: bpy.props.StringProperty(
        name="Event 1",
        default=""
    )

    eventall0_name: bpy.props.StringProperty(
        name="EventAll 0",
        default=""
    )

    eventall1_name: bpy.props.StringProperty(
        name="EventAll 1",
        default=""
    )

    eventall2_name: bpy.props.StringProperty(
        name="EventAll 2",
        default=""
    )

    isolated_name: bpy.props.StringProperty(
        name="Isolated",
        default=""
    )

    overhead: bpy.props.StringProperty(
        name="Overhead",
        default="",
    )

    angle1: bpy.props.FloatProperty(
        name="Angle 1",
        unit="ROTATION",
    )

    angle2: bpy.props.FloatProperty(
        name="Angle 2",
        unit="ROTATION",
    )

    fouling1: bpy.props.FloatProperty(
        name="Fouling 1",
        unit="LENGTH",
    )

    fouling2: bpy.props.FloatProperty(
        name="Fouling 2",
        unit="LENGTH",
    )

    railprofile: bpy.props.StringProperty(
        name="Rail Profile",
        default="",
        update=None,
    )

    friction_memcell: bpy.props.StringProperty(
        name="Friction Memcell",
        default="none",
    )



