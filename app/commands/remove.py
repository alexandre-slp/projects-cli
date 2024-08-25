import subprocess

import click

import app.utils.local as local


async def remove_app_command(app_name: str, org_name: str):
    installation_path = local.INSTALLATION_FOLDER.joinpath(org_name).joinpath(app_name).resolve()
    if not installation_path.exists():
        click.secho(f'App "{app_name}" already removed.', fg='yellow')
        return

    confirm_text = click.style(f'By removing the "{app_name}" app '
                               f'all contents of ({installation_path}) will be removed.\n'
                               f'Are you sure?', bold=True)
    is_sure = click.confirm(confirm_text)
    if not is_sure:
        click.secho(f'Operation aborted.', fg='yellow')
        return

    subprocess.run(f'rm -rf {installation_path}', shell=True, check=True)
    click.secho(f'App "{app_name}" was removed.', fg='green')
