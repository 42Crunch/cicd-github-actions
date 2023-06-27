import jsonpointer # type: ignore
import ruamel.yaml
from ruamel.yaml.comments import CommentedMap

from xliic_cli.helpers.errors import TaskError


def parse_file(path: str) -> CommentedMap:
    with open(path) as f:
        if path.endswith(".yaml") or path.endswith(".yml") or path.endswith(".json"):
            return ruamel.yaml.round_trip_load(f)
        else:
            raise TaskError(f"File at {path} is neither JSON or YAML")


def get_line_and_col(json_pointer: str, parsed_file: CommentedMap):
    value = jsonpointer.resolve_pointer(parsed_file, json_pointer)
    line_no = value.lc.line
    col_no = value.lc.col
    return line_no, col_no
