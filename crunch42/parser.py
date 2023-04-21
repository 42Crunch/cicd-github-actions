import jsonpointer
import ruamel.yaml

def parseFile(path):
    with open(path) as f:
        if path.endswith('.yaml') or path.endswith('.yml'):
            return ruamel.yaml.round_trip_load(f)
        elif path.endswith('.json'):

            return ruamel.yaml.round_trip_load(f)
        else:
            raise ValueError(f"File at {path} is neither JSON or YAML")


def getLineAndCol(jsonPointer, parsedFile):
    value = jsonpointer.resolve_pointer(parsedFile, jsonPointer)
    line_no = value.lc.line
    col_no = value.lc.col
    return line_no, col_no