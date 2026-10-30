"""
Parameters (p1), (p2) ... of included files: the simulator puts the values an include gives them in place of them in the
tokens of the file, and so does the import, so that the names (the hierarchy), the paths and the numbers of an included file
are what the simulator makes of them. What the file holds goes back to it on the export:
- the names of the submodels, whole or parts of them: the T3D Properties of an object keep the name as written in the file
  (Name Template), which goes to the file while the object has the name the parameters of its include give it;
- the elements of the transform matrices: the T3D Properties hold them as Transform Parameters, "index=token" pairs, the
  index of the element in the order of the Transform of the model (0-15), or x, y, z for the translation (12, 13, 14),
  e.g. "x=(p2) y=(p3) z=(p4)". They go to the file in place of the values of the matrix.
"""

from .. import eu07_tools
from ..common.utils import remove_name_suffix
from ..common import includes

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


def include_values(obj):
    """ The values the include of the object gave the parameters of its file on the import ([] for the main file) """
    if obj is None or obj.eu07_include_identifier == includes.MASTER_IDENTIFIER:
        return []
    include = includes.get_include_by_identifier(obj.eu07_include_identifier)
    if include is None:
        return []
    return (include.resolved_parameters or include.parameters).split()


def name_template(obj):
    """ The name of the object as written in its file, with parameters, while the object has the name they give it """
    template = obj.t3d_properties.name_template
    if not template or substitute(template, include_values(obj)) != obj.name:
        return None
    return template


def apply_name_templates(submodels, obj):
    """ The names of the submodels of the object (its parts of materials as well) and of its parent, as written in the
    file, when they hold parameters. The parent's only from the same file: another file sees the name its own include gives """
    names = {obj.name, remove_name_suffix(obj.name)}
    template = name_template(obj)
    parent = obj.parent
    parent_template = None
    if parent is not None and parent.eu07_include_identifier == obj.eu07_include_identifier:
        parent_template = name_template(parent)
    parent_names = {parent.name, remove_name_suffix(parent.name)} if parent is not None else set()
    for submodel in submodels:
        if template:
            if submodel.name in names:
                submodel.name = template
            else:
                for name in names:
                    if submodel.name.startswith(name + "_part"):
                        submodel.name = template + submodel.name[len(name):]
                        break
            if submodel.parent_name in names:
                submodel.parent_name = template
        if parent_template and submodel.parent_name in parent_names:
            submodel.parent_name = parent_template


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
