import subprocess

import click

from app.utils.local import get_app_instructions, get_app_path_interactively


async def stop_app_command(app_name: str, org_name: str):
    app_path = await get_app_path_interactively(app_name, org_name)
    instructions = await get_app_instructions(app_path)
    subprocess.run(instructions['stop'], shell=True, check=True)
    click.secho(f'App "{app_name}" was stopped.', fg='green')
