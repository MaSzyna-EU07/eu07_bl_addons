class ShaderParser:
    def __init__(self, asset_searcher):
        self.asset_searcher = asset_searcher

    def parse_from_abspath(self, abspath, shader_data=None):
        data = ShaderInputs() if shader_data is None else shader_data

        with open(abspath, "r") as shaderfile:
            for line in shaderfile:
                if line.startswith("#include"):
                    _, shader_name = line.strip(" >").split("<")
                    shader_name = shader_name
                    abspath = self.asset_searcher.shaders.find(shader_name)
                    if abspath:
                        self.parse_from_abspath(abspath, data)

                if line.startswith("#texture"):
                    _, defstring = line.split("(")
                    name, location, components = [p.strip() for p in defstring.split(",")]

                    data.textures.append(ShaderTextureInput(name, int(location), components))

                if line.startswith("#param"):
                    _, defstring = line.split("(")
                    name, location, offset, size, default = [p.strip() for p in defstring.split(",")]

                    data.params.append(ShaderParamInput(name, int(location), int(offset), int(size), default))

        return data


class ShaderInputs:
    def __init__(self):
        self.textures = []
        self.params = []


class ShaderTextureInput:
    def __init__(self, name, location, components):
        self.name = name
        self.location = location
        self.components = components

    @property
    def unit_index(self):
        return self.location + 1


class ShaderParamInput:
    def __init__(self, name, location, offset, size, default):
        self.name = name
        self.location = location
        self.offset = offset
        self.size = size
        self.default = default