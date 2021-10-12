import bpy
import bpy_extras


class BaseModelImporter(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    skin_1: bpy.props.StringProperty(
        name="Skin #1",
    )
    skin_2: bpy.props.StringProperty(
        name="Skin #2",
    )
    skin_3: bpy.props.StringProperty(
        name="Skin #3",
    )
    skin_4: bpy.props.StringProperty(
        name="Skin #4",
    )
    import_meshes: bpy.props.BoolProperty(
        name="Import Meshes",
        default=True,
    )
    import_spots: bpy.props.BoolProperty(
        name="Import FreeSpotLights",
        default=True
    )
    import_stars: bpy.props.BoolProperty(
        name="Import Stars",
        default=True
    )
    merge_all: bpy.props.BoolProperty(
        name="Merge to single mesh",
        default=False,
        options={'HIDDEN'}
    )
    link_merged_object: bpy.props.BoolProperty(
        name="Link merged object to scene collection",
        default=True,
        options={'HIDDEN'}
    )

    def _get_replacableskins(self):
        return {
            "replacableskin": self.skin_1,
            "-1": self.skin_1,
            "-2": self.skin_2,
            "-3": self.skin_3,
            "-4": self.skin_4,
        }