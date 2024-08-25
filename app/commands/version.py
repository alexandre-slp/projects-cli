import click

from app.__version__ import __version__


async def show_app_version_command():
    click.secho(f'App version: {__version__}.', fg='green')
