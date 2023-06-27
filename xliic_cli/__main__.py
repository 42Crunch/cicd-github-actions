import os
import typer
import sentry_sdk

from xliic_cli.api_discover import setup_cli as setup_api_discover_cli
from xliic_cli.scan.cli import setup_cli as setup_scan_cli


if os.environ.get("DEBUG", False):
    sentry_sdk.init(
        dsn="https://28cb5859cc6b48fab65af8a341fa089f@o281130.ingest.sentry.io/4505227146756096",
        traces_sample_rate=1.0
    )

app = typer.Typer()


def main():
    setup_api_discover_cli(app)
    setup_scan_cli(app)

    app()


if __name__ == "__main__":
    main()
