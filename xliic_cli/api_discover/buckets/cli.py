import json
import typer

from dataclasses import asdict

from xliic_cli.helpers import print_error_message, print_success_message, print_prompt_message, print_ok_message, \
    print_fail_message

from .app import *


app = typer.Typer()


@app.command(name="list")
def _list():
    """List all buckets"""

    print_prompt_message("Getting buckets list", nl=False)

    try:
        buckets = list_buckets()
        buckets_dict = [asdict(bucket) for bucket in buckets]
        buckets_json = json.dumps(buckets_dict, indent=4)

    except Exception as e:
        print_fail_message()
        print_error_message(str(e))
        raise typer.Abort()

    print_ok_message()
    print_prompt_message(buckets_json, prefix=False)


@app.command(name="create")
def _create(
        name: str = typer.Argument(..., help="Name of the bucket"),
        host: str = typer.Argument(..., help="Host of the bucket"),
        description: str = typer.Option("", "--description", "-d", help="Description of the bucket"),
        base_path: str = typer.Option("/*", "--base-path", "-b", help="Base path of the bucket to create"),
        protocol_http: bool = typer.Option(False, "--http", "-h", help="Enable HTTP protocol"),
        protocol_https: bool = typer.Option(True, "--https", "-s", help="Enable HTTPS protocol"),
):
    """Create a bucket"""

    try:
        bucket_id = create_bucket(name, host, description=description, base_path=base_path,
                                  protocol_http=protocol_http, protocol_https=protocol_https)
    except Exception as e:
        print_error_message(str(e))
        raise typer.Abort()

    bucket_info = {
        "id": bucket_id
    }

    print_success_message(f"Bucket created successfully")
    print_prompt_message(json.dumps(bucket_info, indent=4), prefix=False)


@app.command(name="delete")
def _delete(
        bucket_id: str = typer.Argument(..., help="id of the bucket to delete"),
):
    """Delete a bucket"""

    print_prompt_message(f"Deleting bucket {bucket_id}", nl=False)

    try:
        delete_bucket(bucket_id)
    except Exception as e:
        print_fail_message()
        print_error_message(str(e))
        raise typer.Abort()

    print_ok_message()
    print_success_message(f"Bucket {bucket_id} deleted")


@app.command(name="get")
def _get(
        bucket_id: str = typer.Argument(..., help="Name of the bucket to get"),
):
    """Get a bucket"""

    print_prompt_message(f"Getting bucket {bucket_id}", nl=False)

    try:
        bucket = get_bucket(bucket_id)
        bucket_dict = asdict(bucket)
        bucket_json = json.dumps(bucket_dict, indent=4)
    except Exception as e:
        print_fail_message()
        print_error_message(str(e))
        raise typer.Abort()

    print_ok_message()
    print_prompt_message(bucket_json, prefix=False)


@app.command(name="upload-file")
def _upload_file(
        bucket_id: str = typer.Argument(..., help="id of the bucket to upload file"),
        file_path: str = typer.Argument(..., help="path of the file to upload"),
):
    """Upload a file to a bucket"""

    print_prompt_message(f"Uploading file {file_path} to bucket {bucket_id}", nl=False)

    try:
        upload_file(bucket_id, file_path)
    except Exception as e:
        print_fail_message()
        print_error_message(str(e))
        raise typer.Abort()

    print_ok_message()
    print_success_message("File uploaded")


def setup_cli(_app: typer.Typer):
    _app.add_typer(app, name="bucket", help="Manage buckets")


__all__ = ("setup_cli",)
