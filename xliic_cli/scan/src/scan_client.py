import json
import time
import base64

import docker  # type: ignore
import requests

from xliic_cli.helpers.errors import ScanError
from xliic_cli.helpers.constants import SCAN_MAX_RETRY_TIME, SCAN_RETRY_TIME


class ScanClient:
    def __init__(self, api_key: str, platform_url: str):
        self.api_key = api_key
        self.platform_url = platform_url
        self.headers = _get_headers(api_key)

    def read_default_scan_id(self, api_id: str) -> str:
        try:
            url = _get_url(f"api/v2/apis/{api_id}/scanConfigurations", self.platform_url)

            start_time = time.time()
            while time.time() <= start_time + SCAN_MAX_RETRY_TIME:
                response = requests.get(url, headers=self.headers)
                if response.ok and response.json().get("list", []):
                    return response.json()["list"][0]["configuration"]["id"]
                else:
                    time.sleep(SCAN_RETRY_TIME)

            raise Exception("Request timeout")
        except Exception as e:
            raise ScanError(
                f"Can't read list configuration for API with id {api_id}", str(e))

    def get_technical_name_by_api_id(self, api_id: str) -> str:
        try:
            url = _get_url(f"/api/v1/apis/{api_id}", self.platform_url)

            response = requests.get(url, headers=self.headers)
            if response.ok:
                response_json = response.json()
                return response_json.get("desc").get("technicalName")
            else:
                raise Exception(response.text)
        except Exception as e:
            raise ScanError(
                f"Can't read API with id {api_id}", str(e))

    def create_default_scan_configuration(self, api_id: str) -> str:
        try:
            url = _get_url(f"api/v2/apis/{api_id}/scanConfigurations/default", self.platform_url)
            data = {"name": "default"}
            response = requests.post(url, headers=self.headers, json=data)
            if response.ok:
                response_json = response.json()
                return response_json.get("id")
            else:
                raise Exception(response.text)
        except Exception as e:
            raise ScanError(
                f"Can't get configuration for api with id {api_id}", str(e))

    def read_scan_configuration(self, config_id: str) -> dict:
        try:
            url = _get_url(f"api/v2/scanConfigurations/{config_id}", self.platform_url)
            response = requests.get(url, headers=self.headers)
            if response.ok:
                return response.json()
            else:
                raise Exception(response.text)
        except Exception as e:
            raise ScanError(
                f"Can't read scan configuration with id {config_id}", str(e))

    def wait_scan_report(self, api_id: str) -> str:
        try:
            url = _get_url(f"api/v2/apis/{api_id}/scanReports", self.platform_url)
            start_time = time.time()
            while time.time() <= start_time + SCAN_MAX_RETRY_TIME:
                response = requests.get(url, headers=self.headers)
                if response.ok and response.json().get("list", []):
                    newest_task_id = None
                    newest_start = float('-inf')

                    for obj in response.json()["list"]:
                        if 'report' in obj and 'start' in obj['report']:
                            start_timestamp = float(obj['report']['start'])
                            if start_timestamp > newest_start:
                                newest_start = start_timestamp
                                newest_task_id = obj["report"].get("taskId", None)

                    if newest_task_id:
                        return newest_task_id
                    else:
                        raise Exception(response.text)
                else:
                    time.sleep(SCAN_RETRY_TIME)
            raise Exception(response.text)
        except Exception as e:
            raise ScanError(
                f"Can't read list of scan reports for api_id {api_id}", str(e))

    def read_scan_report(self, task_id: str) -> dict:
        try:
            url_v1 = _get_url(f"api/v1/scanReports/{task_id}", self.platform_url)
            url_v2 = _get_url(f"api/v2/scanReports/{task_id}", self.platform_url)
            response = requests.get(url_v2, headers=self.headers)
            if "message" in response.json() and response.json()["message"] == "invalid authorization":
                response = requests.get(url_v1, headers=self.headers)
            if response.ok:
                return json.loads(
                    base64.b64decode(response.json()["file"].encode("utf-8")).decode(
                        "utf-8"
                    )
                )
            else:
                raise Exception(response.text)
        except Exception as e:
            raise ScanError(
                f"Can't read scan report with id {task_id}", str(e))

    def get_scan_sqgs(self) -> dict:
        try:
            url = _get_url("/api/v2/sqgs/scan", self.platform_url)
            response = requests.get(url, headers=self.headers)
            if response.ok:
                return response.json()
            else:
                raise Exception(response.text)
        except Exception as e:
            raise ScanError("Can't read scan sqg's", str(e))

    def run_scan_docker(self,
                        scan_token: str, image: str = "42crunch/scand-agent:v2.0.0-rc07",
                        service_api: str = "services.dev.42crunch.com:8001"):
        try:
            client = docker.from_env()
            env_vars = {
                "SCAN_TOKEN": scan_token,
                "PLATFORM_SERVICE": service_api,
            }
            container = client.containers.run(
                image, environment=env_vars, detach=True
            )
            container.wait()
            print(container.logs().decode("utf-8"))  # TODO: review
        except Exception as e:
            raise ScanError(
                "Scan Please make sure you have Docker installed and running.", str(e))

    def get_scan_compliance(self, task_id: str) -> dict:
        try:
            url = _get_url("/api/v2/sqgs/reportComplianceStatus", self.platform_url)
            response = requests.get(
                url, headers=self.headers, params={
                    "reportType": "scan", "taskId": task_id}
            )
            if response.ok:
                return response.json()
            else:
                raise Exception(response.text)
        except Exception as e:
            raise ScanError(
                f"Can't read sqg compliance for task {task_id}", str(e))

    def check_sqg(self, sqgs: dict, compl: dict) -> str | None:
        try:
            if "processingDetails" in compl:
                errors: list[str] = []
                for details in compl["processingDetails"]:
                    for sqg in sqgs["list"]:
                        if sqg["id"] == details["blockingSqgId"]:
                            name = sqg["name"]
                            blockingRules = details["blockingRules"]
                            errors.append(
                                f'\t   Fail SQG "{name}", blocking by rules: {blockingRules}'
                            )
                if errors:
                    return "\n".join(str(item) for item in errors)
        except Exception as e:
            raise ScanError("Problem with parsing for check SQG's", str(e))


def _get_headers(api_key: str) -> dict:
    return {"Content-Type": "application/json", "X-API-KEY": api_key}


def _get_url(path: str, platform_url: str) -> str:
    return f"{platform_url}/{path}"
