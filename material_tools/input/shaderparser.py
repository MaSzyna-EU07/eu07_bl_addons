class ShaderParser:
    def __init__(self, asset_searcher):
        self.asset_searcher = asset_searcher

    def parse_from_abspath(self, abspath, shader_data=None):
        data = ShaderData() if shader_data is None else shader_data

        with open(abspath, "r") as shaderfile:
            for line in shaderfile:
                if line.startswith("#include"):
                    print(line)
                    _, shader_name = line.strip().split("<")
                    shader_name = shader_name[:-1]
                    print(shader_name)
                    abspath = self.asset_searcher.shaders.find(f"mat_{shader_name}")
                    if abspath:
                        self.parse_from_abspath(abspath, data)

                if line.startswith("#texture"):
                    _, defstring = line.split("(")
                    alias, index, colorspace = [p.strip() for p in defstring.split(",")]

                    data.alias_map[alias] = int(index) + 1

        return data


class ShaderData:
    def __init__(self):
        self.alias_map = {}