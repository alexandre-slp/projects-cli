import subprocess

import click

import local
import repo


async def install_app_command(app_name: str, org_name: str, is_http):
    installation_path = local.INSTALLATION_FOLDER.joinpath(org_name).joinpath(app_name).resolve()
    if installation_path.exists():
        click.secho(f'App "{app_name}" already installed.', fg='yellow')
        return

    app_repo_url = await repo.get_organization_app_url(app_name, org_name, is_http)
    subprocess.run(f'git clone {app_repo_url} {installation_path}', shell=True, check=True)
