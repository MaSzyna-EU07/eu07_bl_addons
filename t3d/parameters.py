"""
Parameters (p1), (p2) ... of included files: the simulator puts the values an include gives them in place of them in the
tokens of the file. In the models they are in the names of the submodels (whole names or parts of them), which keep them as
they are, and in the elements of the transform matrices, which the T3D Properties of an object hold as Transform
Parameters: "index=token" pairs, the index of the element in the order of the Transform of the model (0-15), or x, y, z
for the translation (12, 13, 14), e.g. "x=(p2) y=(p3) z=(p4)".
"""

from .. import eu07_tools

AXES = {"x": 12, "y": 13, "z": 14}
AXIS_NAMES = {index: axis for axis, index in AXES.items()}


def parse_transform_params(text):
    """ Transform Parameters of the T3D Properties to {index: token} """
    params = {}
    for item in text.split():
        key, separator, token = item.partition("=")
        if not separator or not token:
            continue
        key = key.strip().lower()
        index = AXES.get(key)
        if index is None:
            try:
                index = int(key)
            except ValueError:
                continue
        if 0 <= index < 16:
            params[index] = token.strip()
    return params


def format_transform_params(params):
    """ {index: token} to Transform Parameters of the T3D Properties """
    return " ".join(f"{AXIS_NAMES.get(index, index)}={token}" for index, token in sorted(params.items()))


def substitute(token, parameters):
    return eu07_tools.utils.substitute_parameters(token, parameters)


def resolve_submodel(submodel, parameters):
    """ Puts the values of the parameters of an include in the name, the parent name and the transform of a submodel of the
    included file written into the main one (Aggregate Includes). A parameter which the include passes on as a parameter of
    the main file stays as one; one whose value isn't a number leaves the value of the matrix as it is """
    if not parameters:
        return
    submodel.name = substitute(submodel.name, parameters)
    submodel.parent_name = substitute(submodel.parent_name, parameters)
    params = {}
    for index, token in getattr(submodel, "transform_params", {}).items():
        value = substitute(token, parameters)
        if eu07_tools.utils.has_parameters(value):
            params[index] = value
            continue
        try:
            submodel.transform[index] = float(value)
        except ValueError:
            pass
    submodel.transform_params = params
