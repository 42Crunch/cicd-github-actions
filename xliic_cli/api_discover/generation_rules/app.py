from typing import List

from xliic_cli.helpers import http_get, http_post, http_delete, match_uuid
from xliic_cli.api_discover.generation_rules.models import GenerationRule

from .parsers import get_conf_from_file


class API_PATHS:
    CREATE_RULE = "/api/release/1.0/generation-rules/create/"
    LIST_RULES = "/api/release/1.0/generation-rules/list/"
    GET_DELETE_UPDATE_RULE = "/api/release/1.0/generation-rules/{rule_id}/"
    CREATE_ANALYSIS = "/api/release/1.0/generation-rules/{rule_id}/analysis/"


def get_rule(rule_id: str) -> GenerationRule:
    if not match_uuid(rule_id):
        raise Exception("Invalid bucket id")

    try:
        response = http_get(API_PATHS.GET_DELETE_UPDATE_RULE.format(rule_id=rule_id))
    except Exception as e:
        raise Exception(f"Error getting rule, {e}")

    if response.status_code == 200:
        res = response.json()
        return GenerationRule(**res)
    else:
        raise Exception(f"Error getting rule, {response.reason}")


def get_base_openapi(rule_id: str) -> dict:
    if not match_uuid(rule_id):
        raise Exception("Invalid rule_id id")

    return get_rule(rule_id).openapi_base.get("spec", {})


def list_rules(bucket_id: str) -> List[GenerationRule]:
    if not match_uuid(bucket_id):
        raise Exception("Invalid bucket id")

    try:
        response = http_get(API_PATHS.LIST_RULES, params={"bucket_id": bucket_id})
    except Exception as e:
        raise Exception(f"Error listing rules, {e}")

    if response.status_code == 200:
        resp = response.json()
        return [GenerationRule(**rule) for rule in resp]
    else:
        raise Exception(f"Error listing rules, {response.reason}")


def delete_rule(rule_id: str) -> None:
    if not match_uuid(rule_id):
        raise Exception("Invalid bucket id")

    try:
        response = http_delete(API_PATHS.GET_DELETE_UPDATE_RULE.format(rule_id=rule_id))
    except Exception as e:
        raise Exception(f"Error deleting rule, {e}")

    if response.status_code != 200:
        raise Exception(f"Error deleting rule, {response.reason}")


def create_rule(bucket_id: str, name: str, config_file: dict, description: str = "", extra_data=None) -> str:
    if not match_uuid(bucket_id):
        raise Exception("Invalid bucket id")

    if extra_data is None:
        extra_data = {}

    configuration = get_conf_from_file(config_file)

    request_body = {
        "rule_name": name,
        "description": description,
        "configuration": configuration,
        "extra_data": extra_data,
        "bucket_id": bucket_id
    }

    try:
        response = http_post(API_PATHS.CREATE_RULE, req_body=request_body)
    except Exception as e:
        raise Exception(f"Error creating rule {e}")

    if response.status_code == 200:
        res = response.json()
        return res["generation_rule_id"]
    else:
        raise Exception(f"Error creating rule {response.reason}")


def create_analysis(generation_rule_id: str, extra_data=None) -> str:
    if extra_data is None:
        extra_data = {}

    request_body = {
        "extra_data": extra_data
    }

    try:
        response = http_post(API_PATHS.CREATE_ANALYSIS.format(rule_id=generation_rule_id), req_body=request_body)
    except Exception as e:
        raise Exception(f"Error creating analysis, {e}")

    if response.status_code == 200:
        res = response.json()
        return res["analysisId"]
    else:
        # read error message
        error = response.json().get("message")
        if error:
            raise Exception(f"Error creating analysis, {error}")
        else:
            raise Exception(f"Error creating analysis, {response.reason}")


