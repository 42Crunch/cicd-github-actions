import typer
import tempfile
import datetime

from xliic_cli.helpers import print_error_message, print_success_message, print_ok_message, print_fail_message, \
    print_prompt_message

from .proxy import *
from .utils import *


app = typer.Typer()


@app.command(name="start")
def _start(
        # mode: str streaming or file (future)
        port: int = typer.Option(9999, "--port", "-p", help="port to start proxy on"),
):
    """Start proxy """

    har_name = f"har_{datetime.datetime.now()}.har"

    with tempfile.TemporaryDirectory() as temp_dir:
        # create proxy file
        proxy_file_path = os.path.join(temp_dir, "proxy_requests.jsonl")
        with open(proxy_file_path, "w"):
            ...
        os.environ["PROXY_FILE_PATH"] = proxy_file_path

        # start proxy
        print_prompt_message(f"Starting (http/https) proxy on port {port}")

        try:
            start_proxy(port)
        except KeyboardInterrupt:
            print_prompt_message("Proxy stopped by user")
        except Exception as e:
            print_error_message(f"Error while running proxy, {str(e)})")
            raise typer.Abort()

        # create har file
        print_prompt_message("Creating HAR file", nl=False)
        try:
            create_har_file(proxy_file_path, har_name)
        except Exception as e:
            print_fail_message()
            print_error_message("Error creating HAR file")
            print_error_message(str(e))
            raise typer.Abort()

        print_ok_message()
        print_success_message(f"Har file {har_name} created successfully")


def setup_cli(_app: typer.Typer):
    _app.add_typer(app, name="proxy", help="Manage proxy")


__all__ = ("setup_cli",)
