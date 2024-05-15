import asyncio

import click

from app.commands.list import list_apps_command
from app.commands.start import start_app_command
from utils import global_options


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.option('-v', '--verbose', is_flag=True, default=False, help='Show error messages.')
def cli(
        verbose: bool
):
    global_options.VERBOSE = verbose


@cli.command(help='List apps.')
@click.option('-a', '--show-all', is_flag=True, default=False, help='Show apps without instructions.')
def list_apps(
        show_all: bool
):
    global_options.LIST_APPS_WITHOUT_INSTRUCTIONS = show_all
    try:
        asyncio.run(list_apps_command())
    except Exception as exc:
        if global_options.VERBOSE:
            print(f'Error: {exc}')
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
        if global_options.VERBOSE:
            print(f'Error: {exc}')
        exit(1)


if __name__ == '__main__':
    cli()
