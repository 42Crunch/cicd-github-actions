import base64

from typing import List

from .models import Bucket

from xliic_cli.helpers import http_get, http_post, http_delete, match_uuid


class API_PATHS:
    CREATE_BUCKET = "/api/release/1.0/buckets/create/"
    LIST_BUCKETS = "/api/release/1.0/buckets/list/"
    GET_DELETE_UPDATE_BUCKET = "/api/release/1.0/buckets/{bucket_id}/"
    UPLOAD_FILE = "/api/release/1.0/buckets/{bucket_id}/upload-file/"


def get_bucket(bucket_id: str) -> Bucket:
    if not match_uuid(bucket_id):
        raise Exception("Invalid bucket id")

    try:
        response = http_get(API_PATHS.GET_DELETE_UPDATE_BUCKET.format(bucket_id=bucket_id))
    except Exception as e:
        raise Exception(f"Error getting bucket {e}")

    if response.status_code == 200:
        res = response.json()
        return Bucket(**res)
    else:
        raise Exception(f"Error getting bucket {response.reason}")


def list_buckets() -> List[Bucket]:
    try:
        response = http_get(API_PATHS.LIST_BUCKETS)
    except Exception as e:
        raise Exception(f"Error listing buckets, {e}")

    if response.status_code == 200:
        resp = response.json()
        return [Bucket(**bucket) for bucket in resp]

    raise Exception(f"Error listing buckets, {response.reason}")


def create_bucket(bucket_name: str, bucket_host: str, protocol_http: bool = False, protocol_https: bool = True,
                  base_path: str = "/*", description="", extra_data=None) -> str:
    if extra_data is None:
        extra_data = {}

    try:
        response = http_post(API_PATHS.CREATE_BUCKET, json={
            "bucket_name": bucket_name,
            "bucket_host": bucket_host,
            "base_path": base_path,
            "protocol_http": protocol_http,
            "protocol_https": protocol_https,
            "description": description,
            **extra_data
        })
    except Exception as e:
        raise Exception(f"Error creating bucket, {e}")

    if response.status_code == 200:
        res = response.json()
        return res["bucket_id"]
    else:
        raise Exception(f"Error creating bucket, {response.reason}")


def delete_bucket(bucket_id: str) -> None:
    if not match_uuid(bucket_id):
        raise Exception("Invalid bucket id")

    try:
        response = http_delete(API_PATHS.GET_DELETE_UPDATE_BUCKET.format(bucket_id=bucket_id))
    except Exception as e:
        raise Exception(f"Error deleting bucket, {e}")

    if response.status_code != 200:
        raise Exception(f"Error deleting bucket, {response.reason}")


def upload_file(bucket_id: str, file_path: str):
    if not match_uuid(bucket_id):
        raise Exception("Invalid bucket id")

    file_name = file_path.split("/")[-1]
    file_extension = f".{file_name.split('.')[-1]}"

    with open(file_path, "rb") as file:
        file_content = file.read()
        file_content_base64 = base64.b64encode(file_content).decode('utf-8')

    if file_extension in [".json", ".zip", ".bz2", "tar.bz2", ".tar.gz", ".tgz", "gz"]:
        file_format = "postman"
    elif file_extension in [".log"]:
        file_format = "logs_42c"
    elif file_extension in [".har"]:
        file_format = "har"
    elif file_extension in [".pcap"]:
        file_format = "pcap"
    else:
        raise Exception("Error uploading file, Invalid file extension")

    # file content in base64
    req_body = {
        "file_name": file_name,
        "file_content": file_content_base64,
        "file_extension": file_extension,
        "file_format": file_format
    }

    try:
        response = http_post(API_PATHS.UPLOAD_FILE.format(bucket_id=bucket_id), req_body=req_body)
    except Exception as e:
        raise Exception(f"Error uploading file, {e}")

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error uploading file, {response.reason}")


__all__ = ("API_PATHS", "list_buckets", "get_bucket", "create_bucket", "delete_bucket", "upload_file")
