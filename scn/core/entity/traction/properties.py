import bpy

from . import callbacks

from .....scn.core.entity.node import NodeProperties

class TractionProperties(NodeProperties):
    power_supply_name: bpy.props.StringProperty(
        name="Power Supply Name",
        default="none",
    )

    nominal_voltage: bpy.props.FloatProperty(
        name="Nominal Voltage",
        default=0,
    )

    max_current: bpy.props.FloatProperty(
        name="Max Current",
        default=0,
    )

    resistivity: bpy.props.FloatProperty(
        name="Resistivity",
        default=0,
    )

    material: bpy.props.EnumProperty(
        name="Material",
        items=[
            ("Cu", "Cu", "Copper"),
            ("Al", "Al", "Aluminium"),
        ]
    )

    wire_thickness: bpy.props.FloatProperty(
        name="Thickness",
        default=1,
    )

    damage_flag: bpy.props.IntProperty(
        name="Damage flag",
        default=0
    )

    p1: bpy.props.FloatVectorProperty(
        name="P1",
        size=3,
        get=callbacks.get_p1,
        set=callbacks.set_p1,
    )

    p2: bpy.props.FloatVectorProperty(
        name="P2",
        size=3,
        get=callbacks.get_p2,
        set=callbacks.set_p2,
    )

    p3: bpy.props.FloatVectorProperty(
        name="P3",
        size=3,
        get=callbacks.get_p3,
        set=callbacks.set_p3,
    )

    p4: bpy.props.FloatVectorProperty(
        "P4",
        size=3,
        get=callbacks.get_p4,
        set=callbacks.set_p4,
    )

    min_height: bpy.props.FloatProperty(
        name="Min. height"
    )

    segment_length: bpy.props.FloatProperty(
        name="Segment length"
    )

    wires: bpy.props.IntProperty(
        name="Wires",
        default=2
    )

    wires_offset: bpy.props.FloatProperty(
        name="Wires offset",
        default=0.04
    )

    visible: bpy.props.EnumProperty(
        name="Visible",
        items=(
            ("vis", "vis", "Object is visible"),
            ("unvis", "unvis", "Object is hidden"),
        ),
        default="vis"
    )

    parallel: bpy.props.StringProperty(
        name="Parallel",
        default="none"
    )

classes = (
    TractionProperties,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.eu07_scn_traction = bpy.props.PointerProperty(type=TractionProperties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)