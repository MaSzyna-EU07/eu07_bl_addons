import eu07_tools

class StaticIncludeBankRecord(bpy.types.PropertyGroup):
    relpath: bpy.props.StringProperty()

    params_string: bpy.props.StringProperty()

    mesh: bpy.props.PointerProperty(
        type=bpy.types.Mesh
    )


class StaticIncludeBank(bpy.types.PropertyGroup):
    records: bpy.props.CollectionProperty(
        type=StaticIncludeBankRecord
    )

    def load_from_relpath(self, relpath, parameters):
        params_string = " ".join(str(p) for p in parameters)

        tokenizer = eu07_tools.utils.Tokenizer()


    def get(self, relpath, parameters):
        pass