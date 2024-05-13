import asyncio

import click

from app.commands.list import list_apps_command
from utils import global_options


@click.group(context_settings={'help_option_names': ['-h', '--help']})
def cli():
    pass


@cli.command(help='List apps.')
@click.option('-a', '--show-all', is_flag=True, default=False, help='Show apps without instructions.')
def list_apps(
        show_all: bool
):
    global_options.LIST_APPS_WITHOUT_INSTRUCTIONS = show_all
    try:
        asyncio.run(list_apps_command())
    except Exception as exc:
        print(f'Error: {exc}')
        exit(1)


if __name__ == '__main__':
    cli()
