import json
import re
import typer

from typing import List, Optional
from typing_extensions import Annotated

from xliic_cli.scan.src.scan_client import ScanClient
from xliic_cli.scan.src.sarif_service import produce_sarif_from_scan_reports
from xliic_cli.helpers.report_service import (read_audit_report,
                                              read_audited_ids_from_report)
from xliic_cli.helpers.types_helpers import (print_error_message,
                                             print_fail_message,
                                             print_ok_message,
                                             print_success_message)

app: typer.Typer = typer.Typer()


@app.callback()
def context(
        ctx: typer.Context,
        api_key: str = typer.Option(..., envvar="X42C_API_TOKEN",
                                    help="Set 42Crunch API key"),
        platform_url: str = typer.Option(
            "https://platform.42crunch.com", envvar="X42C_PLATFORM_URL", help="Set 42Crunch platform URL"),
):
    # Create the context object containing the API key and platform URL
    ctx.ensure_object(dict)
    ctx.obj["api_key"] = api_key
    ctx.obj["platform_url"] = platform_url


@app.command(
    "convert-to-sarif",
    short_help="Reads scan report using a JSON report from a file or API identifier, transforms it into a \
        SARIF format, and writes the resulting SARIF file to an output file",
)
def json_report_convert_to_sarif(ctx: typer.Context, sarif_path: str,
                                 report_path: str = typer.Option(None, help="Path to audit json report"),
                                 api_id: Annotated[Optional[List[str]], typer.Option(
                                     help="API identifier provided on the platform")] = None):
    """To convert a scan report to SARIF format using an audit report JSON file or the API identifier
    provided on the platform, you will need to have an existing scan configuration set up and scan report on platform.
    Converting the scan report to SARIF format involves reading the audit report JSON file
    and write SARIF report file.
    """
    if not api_id and not report_path:
        print_error_message("Path to the report or API ID not specified. Please provide the path to the report file "
                            "or specify the API ID.")
        print_fail_message()
        raise typer.Abort()
    api_key = ctx.obj["api_key"]
    platform_url = ctx.obj["platform_url"]
    try:
        audited = {}
        scan_client = ScanClient(api_key, platform_url)
        if api_id:
            for _id in api_id:
                if re.search(r',|\n| ', _id):
                    for _inner_id in [s.strip() for s in re.sub(r", |\n| ", ",", _id).split(",") if s.strip()]:
                        audited[scan_client.get_technical_name_by_api_id(_inner_id)] = _inner_id
                else:
                    audited[scan_client.get_technical_name_by_api_id(_id)] = _id
        elif report_path:
            audit_report = read_audit_report(report_path)
            audited = read_audited_ids_from_report(audit_report)
        scan_reports = {}
        for file, _id in audited.items():
            print(f"Get scan report for file '{file}' with ApiId {_id}")

            #  FOR TEST: IF NEED SCAN REPORT

            # scan_client.create_default_scan_configuration(api_id)
            # scan_id = scan_client.read_default_scan_id(api_id)
            # scan_configuration = scan_client.read_scan_configuration(scan_id)
            # token = scan_configuration["token"]
            # print(f"Got scan token for Api {api_id}")
            # scan_client.run_scan_docker(token)
            # ---
            report_id = scan_client.wait_scan_report(_id)
            report = scan_client.read_scan_report(report_id)
            scan_reports[file] = report
        sarif = produce_sarif_from_scan_reports(scan_reports)
        with open(sarif_path, "w") as outfile:
            json.dump(sarif, outfile, indent=4)
        print_ok_message()
        print_success_message(f"Sarif report was written to the file {sarif_path}")
    except Exception as e:
        print_error_message(str(e))
        print_fail_message()
        raise typer.Abort()


@app.command(
    "check-sqg",
    short_help="Reads scan report using a JSON report from a file or API identifier and checks the SQGs for each API",
)
def json_report_check_sqg(ctx: typer.Context, report_path: str = typer.Option(None, help="Path to audit json report"),
                          api_id: Annotated[Optional[List[str]], typer.Option(help="API identifier provided on the "
                                                                                   "platform")] = None):
    """This command reads a JSON report from a file or use the API identifier
    provided on the platform and checks the SQGs (Security Quality Gates) for each API
    By checking the SQGs against the audit report, this command can determine whether each API
    has passed or failed its security tests.
    """
    api_key = ctx.obj["api_key"]
    platform_url = ctx.obj["platform_url"]
    scan_client = ScanClient(api_key, platform_url)
    if not api_id and not report_path:
        print_error_message("Path to the report or API ID not specified. Please provide the path to the report file "
                            "or specify the API ID.")
        print_fail_message()
        raise typer.Abort()
    try:
        audited = {}
        if api_id:
            for _id in api_id:
                if re.search(r',|\n| ', _id):
                    for _inner_id in [s.strip() for s in re.sub(r", |\n| ", ",", _id).split(",") if s.strip()]:
                        audited[scan_client.get_technical_name_by_api_id(_inner_id)] = _inner_id
                else:
                    audited[scan_client.get_technical_name_by_api_id(_id)] = _id
        elif report_path:
            audit_report = read_audit_report(report_path)
            audited = read_audited_ids_from_report(audit_report)
        sqgs = scan_client.get_scan_sqgs()
        sqg_result = {}
        for file, _id in audited.items():
            task_id = scan_client.wait_scan_report(_id)
            compl = scan_client.get_scan_compliance(task_id)
            errors = scan_client.check_sqg(sqgs, compl)
            if errors is not None:
                sqg_result[file] = errors
        if sqg_result:
            error_message = "The following SQGs failed:\n"
            for file, error in sqg_result.items():
                error_message = error_message + f"\n\t- {file}:\n{error}\n"
            print_error_message(error_message)
            print_fail_message()
            raise typer.Abort()
        print_success_message("All SQGs success")
        print_ok_message()
    except Exception as e:
        print_error_message(str(e))
        print_fail_message()
        raise typer.Abort()


def setup_cli(_app: typer.Typer) -> None:
    _app.add_typer(app, name="scan", help="Work with json report file")


__all__ = ("setup_cli",)
