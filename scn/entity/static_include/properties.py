import bpy

# TODO: This file contains complete, prototype include system. Need to be splitted when ready

# Includ jest obiektem typu empty. Jego dzieckiem jest mesh z wizualizacją.


class StaticIncludeParametersInterface:
    def __init__(self):
        callback_sets = []


class StaticIncludeParameterCallbacks:
    @property
    def callback_set():
        pass

    @property
    def callback_get():
        pass

    @property
    def callback_update():
        pass


def parameter_value_set(self, value):
    identifier = self.id_data.identifier

def parameter_value_get(self):
    identifier = self.id_data.identifier

def parameter_value_update(self, context):
    identifier = self.id_data.identifier


class StaticIncludeParamProperties(bpy.types.PropertyGroup):
    identifier: bpy.props.IntProperty(min=1)

    name: bpy.props.StringProperty()
    description: bpy.props.StringProperty()

    value_int: bpy.props.IntProperty(
        get=parameter_value_get,
        set=parameter_value_set,
        update=parameter_value_update
    )
    value_float: bpy.props.FloatProperty(
        get=parameter_value_get,
        set=parameter_value_set,
        update=parameter_value_update
    )
    value_string: bpy.props.StringProperty(
        get=parameter_value_get,
        set=parameter_value_set,
        update=parameter_value_update
    )

    value_type: bpy.props.EnumProperty(
        name="Value type",
        items=(
            ("integer", "Integer", "Integer"),
            ("float", "Float", "Floating-point number"),
            ("string", "String", "Text value")
        ),
    )


class StaticIncludeProperties(bpy.types.PropertyGroup):
    kind: bpy.types.StringProperty()

    path: bpy.props.StringProperty(
        name="Path",
        subtype="FILE_PATH",
    )

    params: bpy.props.CollectionProperty(
        type=StaticIncludeParamProperties
    )