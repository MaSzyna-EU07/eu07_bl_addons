import bpy

import eu07_tools
from material_tools.utils import get_shortpath_from_material

from . import callbacks


class StaticInclude_TreeProperties(bpy.types.PropertyGroup):
    skin: bpy.props.PointerProperty(
        name="Skin",
        type=bpy.types.Material
    )

    location: bpy.props.FloatVectorProperty(
        name="Location",
        get=callbacks.get_location,
        set=callbacks.set_location,
    )

    rotation: bpy.props.FloatProperty(
        name="Rotation",
        get=callbacks.get_rotation,
        set=callbacks.set_location
    )

    height: bpy.props.FloatProperty(
        name="Height",
        min=0,
        get=callbacks.get_height,
        set=callbacks.set_height,
    )

    span: bpy.props.FloatProperty(
        name="Span",
        min=0,
        get=callbacks.get_span,
        set=callbacks.set_span,
    )

    def get_parameters_list(self):
        return [
            get_shortpath_from_material(self.skin),
            *eu07_tools.utils.swizzle_coords(self.location),
            self.rotation,
            self.height,
            self.span
        ]

    def get_param_string(self):
        return "XXX 0 0 0 0 1 1"


def register():
    bpy.utils.register_class(StaticInclude_TreeProperties)
    bpy.types.Object.eu07_scn_staticinc_tree = bpy.props.PointerProperty(
        type=StaticInclude_TreeProperties
    )


def unregister():
    bpy.utils.unregister_class(StaticInclude_TreeProperties)
    del bpy.types.Object.eu07_scn_staticinc_tree