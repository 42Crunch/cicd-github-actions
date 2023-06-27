import typer

from .auth.cli import setup_cli as setup_auth_cli
from .buckets.cli import setup_cli as setup_buckets_cli
from .quickgen.cli import setup_cli as setup_quickgen_cli
from .generation_rules.cli import setup_cli as setup_generation_rules_cli
from .proxy.cli import setup_cli as setup_proxy_cli

app = typer.Typer()


def setup_cli(_app: typer.Typer) -> None:

    _app.add_typer(app, name="api-discover", help="Manage api_discover")

    setup_auth_cli(app)
    setup_quickgen_cli(app)
    setup_buckets_cli(app)
    setup_generation_rules_cli(app)
    setup_proxy_cli(app)


__all__ = ("setup_cli",)
