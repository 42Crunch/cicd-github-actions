import json
import typer

from dataclasses import asdict

from xliic_cli.helpers import print_error_message, print_success_message, print_prompt_message, print_ok_message, \
    print_fail_message

from .app import *


app = typer.Typer()


@app.command(name="list")
def _list(
    bucket_id: str = typer.Argument(..., help="id of the bucket"),
):
    """List all generation rules associated with a bucket"""

    print_prompt_message("Getting rules list", nl=False)

    try:
        rules = list_rules(bucket_id)
        rules_dict = [asdict(rule) for rule in rules]
        rules_json = json.dumps(rules_dict, indent=4)

    except Exception as e:
        print_fail_message()
        print_error_message(str(e))
        raise typer.Abort()

    print_ok_message()
    print_prompt_message(rules_json, prefix=False)


@app.command(name="delete")
def _delete(
        rule_id: str = typer.Argument(..., help="id of the rule"),
):
    """Delete a generation rule"""

    print_prompt_message(f"Deleting rule {rule_id}", nl=False)

    try:
        delete_rule(rule_id)
    except Exception as e:
        print_fail_message()
        print_error_message(str(e))
        raise typer.Abort()

    print_ok_message()
    print_success_message(f"Rule {rule_id} deleted")


@app.command(name="get")
def _get(
        rule_id: str = typer.Argument(..., help="id of the rule"),
):
    """Get a generation rule"""

    print_prompt_message(f"Getting rule {rule_id}", nl=False)

    try:
        rule = get_rule(rule_id)
        rule_dict = asdict(rule)
        rule_json = json.dumps(rule_dict, indent=4)
    except Exception as e:
        print_fail_message()
        print_error_message(str(e))
        raise typer.Abort()

    print_ok_message()
    print_prompt_message(rule_json, prefix=False)


def setup_cli(_app: typer.Typer):
    _app.add_typer(app, name="generation-rule", help="Manage generation rules")


__all__ = ("setup_cli",)
