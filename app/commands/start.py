import subprocess

import click

from local import get_app_instructions, get_app_path_interactively


async def start_app_command(app_name: str, org_name: str):
    app_path = await get_app_path_interactively(app_name, org_name)
    instructions = await get_app_instructions(app_path)
    subprocess.run(instructions['start'], shell=True, check=True)
    click.secho(f'App "{app_name}" has successfully started.', fg='green')
