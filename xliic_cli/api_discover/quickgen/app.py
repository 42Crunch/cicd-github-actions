from xliic_cli.helpers import http_get, http_post, http_delete
from xliic_cli.api_discover.generation_rules.app import get_base_openapi

from .models import QuickGen


class API_PATHS:
    CREATE_QUICKGEN = "/api/release/1.0/quickgen/new/"
    RECOVER_QUICKGEN = "/api/release/1.0/quickgen/recover/"
    SAVE_QUICKGEN = "/api/release/1.0/quickgen/save/"
    DELETE_QUICKGEN = "/api/release/1.0/quickgen/delete/"


def get_quickgen() -> QuickGen | None:
    try:
        response = http_get(API_PATHS.RECOVER_QUICKGEN)
    except Exception as e:
        raise Exception(f"Error recovering last QuickGen project, {e}")

    if response.status_code == 200:
        res = response.json()
        return QuickGen(**res)
    else:
        raise Exception(f"Error recovering last QuickGen project, {response.reason}")


def get_quickgen_openapi() -> dict:
    quickgen = get_quickgen()
    return get_base_openapi(quickgen.rule_id)


def save_quickgen(bucket_name: str, rule_name: str) -> None:
    request_params = {
        "bucket_name": bucket_name,
        "rule_name": rule_name,
    }

    try:
        response = http_post(API_PATHS.SAVE_QUICKGEN, req_body=request_params)
    except Exception as e:
        raise Exception(f"Error saving current quickgen {e}")

    if response.status_code != 200:
        raise Exception(f"Error saving current quickgen {response.reason}")


def create_quickgen(bucket_id: str, rule_id: str) -> str:
    request_params = {
        "bucket_id": bucket_id,
        "rule_id": rule_id,
    }

    try:
        response = http_post(API_PATHS.CREATE_QUICKGEN, req_body=request_params)
    except Exception as e:
        raise Exception(f"Error creating quickgen {e}")

    if response.status_code != 200:
        raise Exception(f"Error creating quickgen {response.reason}")


def delete_quickgen() -> None:
    try:
        response = http_delete(API_PATHS.DELETE_QUICKGEN)
    except Exception as e:
        raise Exception(f"Error deleting quickgen project, {e}")

    if response.status_code != 200:
        raise Exception(f"Error deleting quickgen project, {response.reason}")


__all__ = ("API_PATHS", "get_quickgen", "save_quickgen", "create_quickgen", "delete_quickgen", "get_quickgen_openapi")
