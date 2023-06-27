import re
import typer

REGEX_UUID_V4 = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$") #TODO: change regex mayus and minus
REGEX_UUID_V4_HEX = re.compile(r"^[0-9a-f]{32}$")


def print_error_message(message: str, nl=True, prefix=True):
    if prefix:
        typer.secho(f"[!] {message}", fg=typer.colors.RED, nl=nl)
    else:
        typer.secho(message, fg=typer.colors.RED, nl=nl)


def print_success_message(message: str, nl=True, prefix=True):
    if prefix:
        typer.secho(f"[+] {message}", fg=typer.colors.GREEN, nl=nl)
    else:
        typer.secho(message, fg=typer.colors.GREEN, nl=nl)


def print_warning_message(message: str, nl=True, prefix=True):
    if prefix:
        typer.secho(f"[!] {message}", fg=typer.colors.YELLOW, nl=nl)
    else:
        typer.secho(message, fg=typer.colors.YELLOW, nl=nl)


def print_prompt_message(message: str, nl=True, prefix=True):
    if prefix:
        typer.secho(f"[*] {message}", fg=typer.colors.WHITE, nl=nl)  # bg=typer.colors.BLUE
    else:
        typer.secho(f"{message}", fg=typer.colors.WHITE, nl=nl)


def print_ok_message():
    typer.secho(" OK", fg=typer.colors.GREEN)


def print_fail_message():
    typer.secho(" FAIL", fg=typer.colors.RED)


def print_not_found_message():
    typer.secho(" NOT FOUND", fg=typer.colors.YELLOW)


def match_uuid(_uuid: str):
    return True if REGEX_UUID_V4.match(_uuid.lower()) or REGEX_UUID_V4_HEX.match(_uuid.lower()) else False


__all__ = ("print_error_message", "print_ok_message", "print_fail_message", "print_prompt_message",
           "print_success_message", "print_warning_message", "print_not_found_message", "match_uuid")
