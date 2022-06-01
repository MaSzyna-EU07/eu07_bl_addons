import bpy

from scn.entity.node import NodeProperties

class TractionProperties(NodeProperties):
    power_supply_name: bpy.types.StringProperty(
        name="Power Supply Name",
        default="none",
    )

    nominal_voltage: bpy.types.FloatProperty(
        name="Nominal Voltage",
        default=0,
    )

    max_current: bpy.types.FloatProperty(
        name="Max Current",
        default=0,
    )

    resistivity: bpy.types.FloatProperty(
        name="Resistivity",
        default=0,
    )

    material: bpy.types.EnumProperty(
        name="Material",
        items=[
            ("Cu", "Cu", "Copper"),
            ("Al", "Al", "Aluminium"),
        ]
    )

    thickness = bpy.types.FloatProperty(
        name="Thickness",
        default=1,
    )