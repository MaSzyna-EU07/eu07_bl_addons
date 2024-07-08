import pathlib

import bpy

import eu07_tools


class RailProfilePoint(bpy.types.PropertyGroup):
    location: bpy.props.FloatVectorProperty(
        size=2,
    )

    normal: bpy.props.FloatVectorProperty(
        size=2,
    )

    mapping: bpy.props.FloatProperty()


class RailProfile(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()

    rail_points: bpy.props.CollectionProperty(
        type=RailProfilePoint
    )

    blade_points: bpy.props.CollectionProperty(
        type=RailProfilePoint
    )


class RailProfileBank(bpy.types.PropertyGroup):
    profiles: bpy.props.CollectionProperty(
        type=RailProfile
    )

    def add_from_name(self, name):
        environment_path = bpy.context.scene.eu07_project_properties.environment_path
        if not environment_path:
            raise ValueError("Environment path not set!")
        profile_path = pathlib.Path(environment_path, "models", "tory", f"railprofile_{name}.txt")

        if not profile_path.exists():
            name = "default"
            profile_path = pathlib.Path(environment_path, "models", "tory", "railprofile_default.txt")

        existing = self.get_profile(name)
        if existing:
            return existing

        return self.add_from_filepath(profile_path, name)


    def add_from_filepath(self, filepath, name):
        with open(filepath) as file:
            return self.add_from_file(file, name)

    def add_from_file(self, file, name):
        existing = self.get_profile(name)
        if existing:
            return existing

        input_profile = eu07_tools.railprofile.load(file)

        try:
            profile = self.profiles.add()
            profile.name = name

            for input_rp in input_profile.rail_points:
                rp = profile.rail_points.add()
                rp.location, rp.normal, rp.mapping = input_rp.location, input_rp.normal, input_rp.mapping

            for input_bp in input_profile.blade_points:
                bp = profile.blade_points.add()
                bp.location, bp.normal, bp.mapping = input_bp.location, input_bp.normal, input_bp.mapping
        except Exception as e:
            self.profiles.remove(profile)
            raise e

        return profile

    def get_profile(self, name):
        if name == "":
            name = "default"

        for profile in self.profiles:
            if profile.name == name:
                return profile



classes = (
    RailProfilePoint,
    RailProfile,
    RailProfileBank,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.eu07_rail_profile_bank = bpy.props.PointerProperty(type=RailProfileBank)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.eu07_rail_profile_bank
    