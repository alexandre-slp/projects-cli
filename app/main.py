import asyncio

import click

from app.commands.list import list_apps_command
from app.commands.start import start_app_command
from app.commands.stop import stop_app_command
from app.commands.install import install_app_command
from app.commands.remove import remove_app_command
from utils import global_options


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.option('-v', '--verbose', is_flag=True, default=False, help='Show more messages.')
def cli(
        verbose: bool
):
    global_options.VERBOSE = verbose


@cli.command(help='List apps.')
@click.option('-a', '--show-all', is_flag=True, default=False, help='Show apps without instructions.')
def list(
        show_all: bool
):
    global_options.LIST_APPS_WITHOUT_INSTRUCTIONS = show_all
    try:
        asyncio.run(list_apps_command())
    except Exception as exc:
        click.secho(f'Error: {exc}', fg='red', bold=True)
        exit(1)


@cli.command(help='Start the app.')
@click.argument('app_name')
@click.option('-o', '--org_name', help='Organization name.')
def start(
        app_name: str,
        org_name: str
):
    try:
        asyncio.run(start_app_command(app_name, org_name))
    except Exception as exc:
        click.secho(f'Error: {exc}', fg='red', bold=True)
        exit(1)


@cli.command(help='Stop the app.')
@click.argument('app_name')
@click.option('-o', '--org_name', help='Organization name.')
def stop(
        app_name: str,
        org_name: str
):
    try:
        asyncio.run(stop_app_command(app_name, org_name))
    except Exception as exc:
        click.secho(f'Error: {exc}', fg='red', bold=True)
        exit(1)


@cli.command(help='Install the app (ssh key by default).')
@click.argument('app_name')
@click.argument('org_name')
@click.option('-t', '--https', 'is_http', is_flag=True, help='Use https clone url.')
def install(
        app_name: str,
        org_name: str,
        is_http: bool,
):
    try:
        asyncio.run(install_app_command(app_name, org_name, is_http))
    except Exception as exc:
        click.secho(f'Error: {exc}', fg='red', bold=True)
        exit(1)


@cli.command(help='Remove the app.')
@click.argument('app_name')
@click.argument('org_name')
def remove(
        app_name: str,
        org_name: str,
):
    try:
        asyncio.run(remove_app_command(app_name, org_name))
    except Exception as exc:
        click.secho(f'Error: {exc}', fg='red', bold=True)
        exit(1)


if __name__ == '__main__':
    cli()
