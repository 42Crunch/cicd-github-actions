import json


def create_har_file(sorted_file_name: str, har_file_name: str):
    har_header = {
        "log": {
            "version": "1.2",
            "creator": {
                "name": "42c-cli",
                "version": "1.0.0"
            },
            "entries": []
        }
    }

    with open(sorted_file_name) as sorted_file:
        data = [json.loads(line) for line in sorted_file]

        for line in data:
            try:
                entry = process_line(line)
            except Exception as e:
                print(e)
                continue
            har_header["log"]["entries"].append(entry)

    with open(har_file_name, mode="w") as writer:
        writer.write(json.dumps(har_header, indent=2))


def process_line(line: dict) -> dict:

    if line["request_query_params"]:
        request_query_params = [{"name": key, "value": value} for key, value in line["request_query_params"].items()]
    else:
        request_query_params = []

    response_content = {
        "mimeType": line["response_headers"].get("Content-Type", "text/plain").split(";")[0],
        "text": line["response_body"],
        "size": line["response_headers"].get("Content-Length", 0),
    }

    entry = {
        "startedDateTime": "2021-08-31T18:00:00.000Z",
        "time": 0,
        "request": {
            "method": line["request_method"],
            "url": line["url"],
            "httpVersion": "HTTP/1.1",
            "cookies": [],
            "headers": [
                {"name": key, "value": value} for key, value in line["request_headers"].items()
            ],
            "queryString": request_query_params,
            "headersSize": 0,
            "bodySize": 0
        },
        "response": {
            "status": line["response_code"],
            "statusText": line["response_reason"],
            "httpVersion": "HTTP/1.1",
            "cookies": [],
            "headers": [
                {"name": key, "value": value} for key, value in line["response_headers"].items()
            ],
            "content": response_content,
            "redirectURL": "",
            "headersSize": 0,
            "bodySize": 0,
            "_transferSize": 0,
            "_error": None
        },
        "cache": {},
        "timings": {
            "blocked": 0,
            "dns": 0,
            "ssl": 0,
            "connect": 0,
            "send": 0,
            "wait": 0,
            "receive": 0,
            "_blocked_queueing": 0
        }
    }

    request_post_data = {
        "mimeType": line["request_headers"].get("Content-Type", "").split(";")[0],
        "text": line["request_body"],
        "params": [],
    }

    if request_post_data["mimeType"] or request_post_data["text"]:
        entry["request"]["postData"] = request_post_data

    return entry


__all__ = ["create_har_file"]
