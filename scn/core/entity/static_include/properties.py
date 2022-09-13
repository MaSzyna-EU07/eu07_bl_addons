import bpy


class StaticIncludeProperties(bpy.types.PropertyGroup):
    subtype: bpy.props.EnumProperty(
        items=[
            ("placeholder", "placeholder", "Placeholder"),
            ("tree", "tree", "Procedural tree"),
        ],
    )

    path: bpy.props.StringProperty(
        name="Path",
        subtype="FILE_PATH",
    )

    @property
    def subprops(self):
        if self.subtype == "placeholder":
            return self.id_data.eu07_scn_staticinc_placeholder
        elif self.subtype == "tree":
            return self.id_data.eu07_scn_staticinc_tree

    def get_parameters_list(self):
        return self.subprops.get_parameters_list()

    def get_param_string(self):
        return self.subprops.get_param_string()

def register():
    bpy.utils.register_class(StaticIncludeProperties)
    bpy.types.Object.eu07_scn_staticinc = bpy.props.PointerProperty(type=StaticIncludeProperties)


def unregister():
    bpy.utils.unregister_class(StaticIncludeProperties)
    del bpy.types.Object.eu07_scn_staticinc



