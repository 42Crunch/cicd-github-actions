import crunch42.scan_service as Scan_service
import crunch42.report_service as report_service
import crunch42.sarif_service as sarif_service
import json
import sys
import click


class PlatformConnection:
    def __init__(self, api_key, platform_url):
        self.api_key = api_key
        self.platform_url = platform_url

    def __platform__(self):
        return f"<Platform url:  {self.config.platform_url}>"


pass_scan = click.make_pass_decorator(PlatformConnection)


@click.group()
@click.option(
    "--api_key",
    required=True,
    envvar="X42C_API_TOKEN",
    help="Set 42Crunch api key",
)
@click.option(
    "--platform_url",
    envvar="X42C_PLATFORM_URL",
    default="https://platform.42crunch.com",
    help="Set 42Crunch platform url",
)
@click.version_option("1.0")
@click.pass_context
def scan(ctx, api_key, platform_url):
    ctx.obj = PlatformConnection(api_key, platform_url)


@click.group("json-report")
def json_report():
    pass


scan.add_command(json_report)


@json_report.command("convert-to-sarif", short_help="Reads a JSON report from a file, transforms it into a SARIF format, and writes the resulting SARIF file to an output file")
@click.argument("report_path")
@click.argument("sarif_path")
@pass_scan
def json_report_convert_to_sarif(scan, report_path, sarif_path):
    """To convert a scan report to SARIF format using an audit report JSON file, 
    you will need to have an existing scan configuration set up and scan report on platform.
    Converting the scan report to SARIF format involves reading the audit report JSON file 
    and write SARIF report file.
    """
    audit_report = report_service.read_audit_report(report_path)
    audited = report_service.read_audited_ids_from_report(audit_report)
    scan_reports = {}
    scan_client = Scan_service.Scan_Client(scan.api_key, scan.platform_url)
    for file, api_id in audited.items():
        # print(f"{file} with ApiId {api_id}")
        # scan_service.create_default_scan_configuration(api_id)
        # scan_id = scan_service.read_default_scanId(api_id)
        # scan_configuration = scan_service.read_scan_configuration(scan_id)
        # token = scan_configuration["token"]
        # print(f"Got scan token for Api {api_id}")
        # scan_service.runScanDocker(token)
        report_id = scan_client.wait_scan_report(api_id)
        report = scan_client.read_scan_report(report_id)
        scan_reports[file] = report
    sarif = sarif_service.produce_sarif_from_scan_reports(scan_reports)
    with open(f"{sarif_path}", "w") as outfile:
        json.dump(sarif, outfile, indent=4)


@json_report.command("check-sqg", short_help="Reads a JSON report from a file and checks the SQGs for each API")
@click.argument("report_path")
@pass_scan
def json_report_check_sqg(scan, report_path):
    """This command reads a JSON report from a file and checks the SQGs (Security Quality Gates) for each API 
    By checking the SQGs against the audit report, this command can determine whether each API 
    has passed or failed its security tests.
    """
    scan_client = Scan_service.Scan_Client(scan.api_key, scan.platform_url)
    report = report_service.read_audit_report(report_path)
    audited = report_service.read_audited_ids_from_report(report)
    sqgs = scan_client.get_scan_SQGS()
    sqg_result = {}
    for file, api_id in audited.items():
        task_id = scan_client.wait_scan_report(api_id)
        compl = scan_client.get_scan_compliance(task_id)
        errors = scan_client.check_sqg(sqgs, compl)
        if errors is not None:
            sqg_result[file] = errors
    if len(sqg_result) > 0:
        print("\nThe following SQGs failed:\n")
        for file, error in sqg_result.items():
            print(f"- {file}:\n{error}\n")
        sys.exit(1)
    sys.exit(0)
