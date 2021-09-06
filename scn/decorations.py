import eu07_tools
import io
import bpy

import io

# analiza kontekstu parametrów:
# - lokacja: 3 tokeny po słowie origin
# - rotacja: 3 tokeny po słowie rotate
# - tekstura:
#   * 4 token po słowie model, o ile słowo model występuje na 4 pozycji po słowie node
#   * 1 token po słowie zawierającym słowo triangle, o ile słowo triagle występuje na 4 pozycji po słowie node;
#   * 1 token po słowie endmaterial

def analyze_inc_parameters_context(inc_file):
    meaning = {
        "location": [],
        "rotation": [],
        "skin": [],
    }

    tokenizer = eu07_tools.utils.Tokenizer() # pass the file directly
    tokens = tokenizer.tokenize_file(inc_file)
    for token in tokens:
        token = token.lower()
        if token == "origin":
            for _ in range(3):
                candidate = next(tokens)
                if "(p" in candidate:
                    meaning["location"].append(int(candidate[2] - 1))
        elif token == "rotate":
            for _ in range(3):
                candidate = next(tokens)
                if "(p" in candidate:
                    meaning["rotation"].append(int(candidate[2] - 1))
        elif token == "node":
            subtype = ""
            for _ in range(4):
                subtype = next(tokens)

            if subtype == "model":
                for _ in range(4):
                    candidate = next(tokens)
                    if "(p" in candidate:
                        meaning["skin"].append(int(candidate[2] - 1))

            elif "triangle" in subtype:
                candidate = next(tokens)
                if "(p" in candidate:
                    meaning["skin"].append(int(candidate[2] - 1))

        elif token == "endmaterial":
            candidate = next(tokens)
            if "(p" in candidate:
                meaning["skin"].append(int(candidate[2] - 1))

    return meaning


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