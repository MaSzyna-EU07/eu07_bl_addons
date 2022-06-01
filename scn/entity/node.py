import bpy

#TODO: Maybe move it to separate module for better organisation (if there will be more callbacks)
def set_name(self, value):
    self.id_data.name = value

def get_name(self):
    return self.id_data.name

class NodeProperties(bpy.types.PropertyGroup):
    max_distance: bpy.props.FloatProperty(
        name="Max Distance",
        default=-1,
        unit="LENGTH",
    )

    min_distance: bpy.props.FloatProperty(
        name="Min Distance",
        default=-1,
        unit="LENGTH",
    )

    name: bpy.props.StringProperty(
        name="Name",
        get=get_name,
        set=set_name,
    )

    

