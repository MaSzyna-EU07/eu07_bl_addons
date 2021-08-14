import eu07_tools
import io
import bpy

class DecorationsBuilder:
    def __init__(self, config):
        self.config = config

    def load_decoration(self, decoration):
        if decoration.typename == "include":
            decoration

        if decoration.typename == "node:model":
            self.load_model(decoration)

    def load_model(self, model):
        path = self.config["asset_searcher"].models.find(model.path)
        if path:
            pass


class DecorationIncludeLoader:
    def __init__(self):
        pass

    def load_include(self, filename, params):
        with open(filename) as incfile:
            content = self.apply_parameters(incfile.read(), params)
            for o in eu07_tools.scn.load(io.StringIO(content)):
                if o.type == "node:model":
                    pass
                    # importujemy model e3d tudziez t3d z podanej sciezki
                    # zaymportowane meshe laczymy w jeden wielki mesh z multimaterialem


    def apply_parameters(self, content, params):
        # TODO: Optimize

        for param_index, param in enumerate(params, start=1):
            content = content.replace(f"(p{param_index}", param)

        return content