from xliic_cli.helpers import parser
from xliic_cli.helpers.errors import ScanError
from xliic_cli.helpers.types_helpers import print_warning_message
from xliic_cli.scan.src.owasp_details import get_owasp_issue_detail_by_id


def produce_sarif_from_scan_reports(scan_reports: dict) -> dict:
    try:
        sarif_artifact_indices = {}
        sarif_results: list[dict] = []
        sarif_files = {}
        next_artifact_index = 0
        next_rule_index = 0
        sarif_rule_indices = {}
        sarif_rules = {}
        sarif_log: dict = {
            "version": "2.1.0",
            "$schema": "http://json.schemastore.org/sarif-2.1.0-rtm.4",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "42Crunch API Conformance Scan",
                            "informationUri": "https://42crunch.com/",
                            "rules": [],
                        },
                    },
                    "results": sarif_results,
                    "artifacts": [],
                },
            ],
        }

        for file_name, report in scan_reports.items():
            if report["summary"]["state"] == "finished":
                for path, path_obj in report["paths"].items():
                    for method, method_obj in path_obj.items():
                        if "conformanceRequestIssues" in method_obj:
                            for issue in method_obj["conformanceRequestIssues"]:
                                test = issue["test"]
                                if file_name not in sarif_files:
                                    next_artifact_index += 1
                                    sarif_artifact_indices[file_name] = next_artifact_index
                                    sarif_files[file_name] = {
                                        "location": {
                                            "uri": file_name,
                                        },
                                    }
                                parsed_file = parser.parse_file(file_name)
                                line, col = parser.get_line_and_col(test["jsonPointer"], parsed_file)
                                sarif_representation = {
                                    "level": "error",
                                    "ruleId": test["key"],
                                    "message": {
                                        "text": test["description"],
                                    },
                                    "locations": [
                                        {
                                            "physicalLocation": {
                                                "artifactLocation": {
                                                    "uri": file_name,
                                                    "index": sarif_artifact_indices[file_name],
                                                },
                                                "region": {
                                                    "startLine": line,
                                                    "startColumn": col,
                                                },
                                            },
                                        },
                                    ],
                                }
                                if not test["key"] in sarif_rules:
                                    next_rule_index += 1
                                    sarif_rule_indices[test["key"]] = next_rule_index
                                    help_url = "https://support.42crunch.com"
                                    help_text = "This is a sample entry for scan issue help"
                                    owasp_details = get_owasp_issue_detail_by_id(test["owaspMapping"])
                                    sarif_rules[test["key"]] = {
                                        "id": test["key"],
                                        "shortDescription": {
                                            "text": test["description"],
                                        },
                                        "helpUri": help_url,
                                        "help": {
                                            "text": f"Owasp issue: {owasp_details.short_name}: {owasp_details.long_name}\nDetails: {help_text}",
                                        },
                                        "properties": {
                                            "owapIssue": owasp_details.long_name,
                                            "category": "Other",
                                        },
                                    }
                                sarif_representation["ruleIndex"] = sarif_rule_indices[test["key"]]
                                sarif_results.append(sarif_representation)
            else:
                print_warning_message(
                    f"Skip {file_name} file - scan process not finished, scan status: {report['summary']['state']}"
                )

        if sarif_files.keys():
            sarif_log["runs"][0]["artifacts"] = []
            for path in sarif_files.keys():
                sarif_log["runs"][0]["artifacts"].append(sarif_files[path])

        if sarif_rules.keys():
            for rule_id in sarif_rules.keys():
                sarif_log["runs"][0]["tool"]["driver"]["rules"].append(sarif_rules[rule_id])

        return sarif_log
    except Exception as e:
        raise ScanError("Can't create sarif report: ", str(e))
