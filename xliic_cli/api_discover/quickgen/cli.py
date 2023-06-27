import os
import time
import json
from dataclasses import asdict

import yaml
import typer
import shutil

from typing import List

from xliic_cli.helpers import print_error_message, print_success_message, print_warning_message, print_prompt_message, \
    print_ok_message, print_fail_message, print_not_found_message

from .app import *
from .parsers import parse_conf_file

from xliic_cli.api_discover.buckets import create_bucket, upload_file
from xliic_cli.api_discover.generation_rules import create_rule, create_analysis, get_base_openapi

app = typer.Typer()

# retry times and delay for openapi generation
retry_times = 5
delay = 2


@app.command(name="create")
def create(
        config_file: str = typer.Argument(..., help="Configuration file path"),
        input_file: List[str] = typer.Argument(..., help="Input file path"),
        output_file: str = typer.Option(None, "--output-file", "-o", help="Output file path")
):
    """Create a QuickGen project"""

    # test if all files exist and if the config file is valid
    if not os.path.exists(config_file):
        print_error_message("Configuration file does not exist")
        raise typer.Abort()

    if len(input_file) < 1:
        print_error_message("Error creating project, no input files provided")
        raise typer.Abort()

    with open(config_file, "r") as f:
        conf_file = yaml.safe_load(f)

    try:
        parse_conf_file(conf_file)
    except Exception as e:
        print_error_message(f"Error parsing conf file {e}")
        raise typer.Abort()

    for in_file in input_file:
        if not os.path.exists(in_file):
            print_error_message(f"Error creating project, input file {in_file} not found")
            raise typer.Abort()

    # delete old quickgen project and related tables

    try:
        quickgen = get_quickgen()
    except Exception as e:
        quickgen = None

    if quickgen:
        print_prompt_message("A quickgen project already exists, cleaning up", nl=False)

        try:
            delete_quickgen()
        except Exception as e:
            print_fail_message()
            print_error_message(str(e))
            raise typer.Abort()

        print_ok_message()

    # create quickgen bucket
    print_prompt_message("Creating quickgen bucket", nl=False)
    try:
        bucket_id = create_bucket(
            bucket_name="quickgen_bucket",
            bucket_host=conf_file.get("host", ""),
            protocol_http=conf_file.get("protocols", {}).get("http", False),
            protocol_https=conf_file.get("protocols", {}).get("https", False),
            base_path=conf_file.get("base_path", "/*"),
            extra_data={"extra_data": {"is_quickgen": True}}
        )
    except Exception as e:
        print_fail_message()
        print_error_message(str(e))
        raise typer.Abort()

    print_ok_message()

    # upload files to bucket
    for in_file in input_file:
        print_prompt_message(f"Uploading file {in_file} to bucket", nl=False)
        try:
            upload_file(bucket_id, in_file)
        except Exception as e:
            print_fail_message()
            print_error_message(str(e))
            raise typer.Abort()
        print_ok_message()
        time.sleep(delay)

    # create quickgen generation rule
    print_prompt_message("Creating quickgen generation rule", nl=False)

    try:
        rule_id = create_rule(
            bucket_id=bucket_id,
            name="quickgen_rule",
            extra_data={"is_quickgen": True},
            config_file=conf_file
        )
    except Exception as e:
        print_fail_message()
        print_error_message(str(e))
        raise typer.Abort()

    print_ok_message()

    # create quickgen project

    print_prompt_message("Creating quickgen project", nl=False)
    try:
        quickgen_id = create_quickgen(
            bucket_id=bucket_id,
            rule_id=rule_id,
        )
    except Exception as e:
        print_error_message(str(e))
        raise typer.Abort()

    print_ok_message()

    # create analysis

    print_prompt_message("Creating new analysis", nl=False)

    try:
        analysis_id = create_analysis(
            generation_rule_id=rule_id,
            extra_data={"is_quickgen": True}
        )
    except Exception as e:
        print_fail_message()
        print_error_message(str(e))
        raise typer.Abort()

    print_ok_message()

    for retry in range(retry_times):
        print_prompt_message(f"Trying to retrieve OpenAPI file...", nl=False)

        try:
            oas = get_base_openapi(rule_id)
        except Exception as e:
            print_fail_message()
            print_error_message(str(e))
            raise typer.Abort()

        if oas and oas.get("openapi"):
            print_ok_message()
            oas_str = json.dumps(oas, indent=4)
            if output_file:
                with open(output_file, "w") as f:
                    f.write(oas_str)
                print_success_message(f"OpenAPI file saved in {output_file}")
            else:
                print_success_message("OpenAPI file retrieved")
                print_prompt_message(oas_str, prefix=False)
            return
        else:
            print_not_found_message()

            print_warning_message("OpenAPI file not ready yet, retrying...")
            time.sleep(delay)

    print_error_message("Error retrieving OpenAPI file, please try again later using get-openapi command")


@app.command(name="delete")
def delete():
    """ Delete current QuickGen project """

    print_prompt_message("Deleting QuickGen project", nl=False)

    try:
        delete_quickgen()
    except Exception as e:
        print_fail_message()
        print_error_message(str(e))
        raise typer.Abort()

    print_ok_message()
    print_success_message("QuickGen project deleted")


@app.command(name="create-config-file")
def create_template():
    """Create a new QuickGen configuration file template"""

    config_file_path = os.path.dirname(os.path.abspath(__file__)) + "/templates/conf_file_template.yaml"

    # test if file exists
    if os.path.exists("./conf_file_template.yaml"):
        print_error_message("Error creating config file template, file already exists")
        raise typer.Abort()

    # copy file
    shutil.copyfile(config_file_path, "./conf_file_template.yaml")

    print_success_message("Config file template created")


@app.command(name="get")
def recover():
    """Recover last QuickGen project"""

    print_prompt_message("Recovering QuickGen project", nl=False)

    try:
        quickgen = get_quickgen()
        quickgen_dict = asdict(quickgen)
        quickgen_json = json.dumps(quickgen_dict, indent=4)
    except Exception as e:
        print_fail_message()
        print_error_message(str(e))
        raise typer.Abort()

    if not quickgen:
        print_warning_message("No QuickGen project found")
        raise typer.Abort()

    print_ok_message()
    print_prompt_message(quickgen_json, prefix=False)


@app.command(name="get-openapi")
def recover_openapi(
        output_file: str = typer.Option(None, "--output-file", "-o", help="Output file path")
):
    """Recover last QuickGen project OpenAPI"""

    print_prompt_message("Recovering QuickGen project OpenAPI", nl=False)

    try:
        oas = get_quickgen_openapi()
        oas_str = json.dumps(oas, indent=4)
    except Exception as e:
        print_fail_message()
        print_error_message(str(e))
        raise typer.Abort()

    if not oas:
        print_not_found_message()
        print_warning_message("The OpenAPI file is not ready yet, try again in a few seconds")
        raise typer.Abort()

    print_ok_message()

    if output_file:
        with open(output_file, "w") as f:
            f.write(oas_str)
        print_success_message(f"OpenAPI file saved in {output_file}")
    else:
        print_prompt_message(oas_str, prefix=False)


@app.command(name="save")
def save(
        bucket_name: str = typer.Argument(..., help="Bucket name"),
        rule_name: str = typer.Argument(..., help="Rule name")
):
    """Save current QuickGen project into a new bucket and rule, this will delete the current QuickGen project"""

    if not bucket_name:
        print_error_message("Bucket name is required")
        raise typer.Abort()

    if not rule_name:
        print_error_message("Rule name is required")
        raise typer.Abort()

    print_prompt_message("Saving QuickGen project", nl=False)

    try:
        save_quickgen(bucket_name, rule_name)
    except Exception as e:
        print_fail_message()
        print_error_message(str(e))
        raise typer.Abort()

    print_ok_message()
    print_success_message("QuickGen project converted successfully and saved")
    # although the quickgen project is deleted, it is better to send a user-friendly message
    print_prompt_message("Deleting QuickGen project", nl=False)
    print_ok_message()


def setup_cli(_app: typer.Typer):
    _app.add_typer(app, name="quickgen", help="Manage quickgen projects")


__all__ = ("setup_cli",)
