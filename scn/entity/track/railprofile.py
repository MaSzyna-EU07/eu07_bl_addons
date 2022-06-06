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

    def get_values(self):
        return [*self.location, *self.normal, *self.mapping]


class RailProfile(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()

    rail_points: bpy.props.CollectionProperty(
        type=RailProfilePoint
    )

    blade_points: bpy.props.CollectionProperty(
        type=RailProfilePoint
    )

    def get_values_list_for_rail(self):
        return [p.get_values() for p in self.rail_points]

    def get_values_list_for_blade(self):
        return [p.get_values() for p in self.blade_points]


class RailProfileBank(bpy.types.PropertyGroup):
    profiles: bpy.props.CollectionProperty(
        type=RailProfile
    )

    def add_from_filepath(self, filepath):
        # TODO: Move name getting to eu07_tools
        name = pathlib.Path(filepath).stem.lstrip("railprofile_")

        with open(filepath, encoding="latin-1") as file:
            self.add_from_file(file, name)

    def add_from_file(self, file, name):
        input_profile = eu07_tools.railprofile.load(file, name)

        profile = self.profiles.add()
        profile.name = name

        for input_rp in input_profile.rail_points:
            rp = profile.rail_points.new()
            rp.location, rp.normal, rp.mapping = input_rp.location, input_rp.normal, input_rp.mapping

        for input_bp in input_profile.blade_points:
            bp = profile.blade_points.new()
            bp.location, bp.normal, bp.mapping = input_bp.location, input_bp.normal, input_bp.mapping