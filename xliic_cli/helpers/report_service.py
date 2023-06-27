import json
import sys

from xliic_cli.helpers.types_helpers import (print_error_message,
                                             print_fail_message,
                                             print_warning_message)


def read_audited_ids_from_report(file: dict) -> dict[str, str]:
    result = {}
    try:
        for key, value in file.items():
            if value["audited"]:
                result[key] = (value["apiId"])
            else:
                print_warning_message(f"Skipped because an API has failed security audit: {key}")
        return result
    except Exception as e:
        print_fail_message()
        print_error_message(f"There was an error parsing the audit report. Please ensure that the file you provided\
                             is the correct audit report file. Error details: {e}")
        sys.exit(1)


def read_audit_report(path: str) -> dict:
    try:
        with open(path, 'r') as f:
            data = json.load(f)

        files = data["audit"]["report"]
        return files
    except Exception as e:
        print_fail_message()
        print_error_message(f"Error uploading audit report \"{path}\" : {e}")
        sys.exit(1)
