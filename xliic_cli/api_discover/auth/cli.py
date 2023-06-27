import typer
import getpass

from xliic_cli.helpers import print_error_message, print_success_message, print_prompt_message, print_ok_message, \
    print_fail_message

from .app import *

app = typer.Typer()


def setup_cli(_app: typer.Typer) -> None:
    @_app.command()
    def login(
            service_url: str = typer.Option("http://localhost:80", "--url", "-u", help="URL of the service to login to"),
            with_browser: bool = typer.Option(False, "--browser", "-b", help="Open the browser to login"),
    ):
        """Login to Horus the platform"""
        if with_browser:
            print_prompt_message("Opening browser")
            login_with_browser(service_url)

        else:
            # Request user / password
            user = input("> User: ")
            password = getpass.getpass("> Password: ")

            print_prompt_message(f"Trying to login to {service_url} with user {user}", nl=False)

        try:
            login_with_terminal(user, password, service_url)
        except Exception as e:
            print_fail_message()
            print_error_message(str(e))
            raise typer.Abort()

        print_ok_message()
        print_success_message(f"Login successful")


__all__ = ("setup_cli",)
