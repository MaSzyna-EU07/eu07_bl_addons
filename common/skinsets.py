import bpy




class EU07SkinSet(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name="Name"
    )

    materials: bpy.props.CollectionProperty(
        type=bpy.types.Material
    )


class EU07_UL_SkinSetsList:
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'RENDERLAYERS'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=f"{item.name}", icon=custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon=custom_icon)


classes = (
    EU07_UL_SkinSetsList,

)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        bpy.types.Scene.eu07_skinsets = bpy.props.CollectionProperty(type=EU07SkinSet)
        bpy.types.Scene.eu07_active_skinset_index = bpy.props.IntProperty(min=0)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)