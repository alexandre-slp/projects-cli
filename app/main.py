import asyncio

import click

from app.commands.cd import cd_app_command
from app.commands.install import install_app_command
from app.commands.list import list_apps_command
from app.commands.remove import remove_app_command
from app.commands.start import start_app_command
from app.commands.stop import stop_app_command
from app.commands.version import show_app_version_command
from utils import global_options


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.option('-v', '--verbose', is_flag=True, default=False, help='Show more messages.')
def cli(
        verbose: bool,
):
    global_options.VERBOSE = verbose


@cli.command(help="Change to app's directory.")
@click.argument('app_name')
@click.option('-o', '--org', 'org_name', help='Organization name.')
def cd(
        app_name: str,
        org_name: str,
):
    try:
        asyncio.run(cd_app_command(app_name, org_name))
    except Exception as exc:
        click.secho(f'Error: {exc}', fg='red', bold=True)
        exit(1)


@cli.command(help='Install the app (ssh key by default).')
@click.argument('app_name')
@click.argument('org_name')
@click.option('-t', '--https', 'is_https', is_flag=True, help='Use https clone url.')
def install(
        app_name: str,
        org_name: str,
        is_https: bool,
):
    try:
        asyncio.run(install_app_command(app_name, org_name, is_https))
    except Exception as exc:
        click.secho(f'Error: {exc}', fg='red', bold=True)
        exit(1)


@cli.command(help='List apps.')
@click.option('-a', '--all', 'show_all', is_flag=True, default=False, help='Show apps without instructions.')
@click.option('-c', '--show-captions', is_flag=True, default=False, help='Show captions.')
def list(
        show_all: bool,
        show_captions: bool,
):
    global_options.LIST_APPS_WITHOUT_INSTRUCTIONS = show_all
    try:
        asyncio.run(list_apps_command(show_captions))
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


@cli.command(help='Start the app.')
@click.argument('app_name')
@click.option('-o', '--org', 'org_name', help='Organization name.')
def start(
        app_name: str,
        org_name: str,
):
    try:
        asyncio.run(start_app_command(app_name, org_name))
    except Exception as exc:
        click.secho(f'Error: {exc}', fg='red', bold=True)
        exit(1)


@cli.command(help='Stop the app.')
@click.argument('app_name')
@click.option('-o', '--org', 'org_name', help='Organization name.')
def stop(
        app_name: str,
        org_name: str,
):
    try:
        asyncio.run(stop_app_command(app_name, org_name))
    except Exception as exc:
        click.secho(f'Error: {exc}', fg='red', bold=True)
        exit(1)


@cli.command(help='Show app version.')
def version():
    try:
        asyncio.run(show_app_version_command())
    except Exception as exc:
        click.secho(f'Error: {exc}', fg='red', bold=True)
        exit(1)


if __name__ == '__main__':
    cli()
