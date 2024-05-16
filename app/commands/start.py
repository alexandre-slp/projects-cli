import pathlib
import subprocess

import click

from local import INSTALLATION_FOLDER, get_organizations, get_app_instructions


async def start_app_command(app_name: str, org_name: str):
    app_path = await get_app_path(app_name, org_name)
    instructions = await get_app_instructions(app_path)
    subprocess.run(instructions['start'], shell=True, check=True)


async def get_app_path(app_name: str, org_name: str) -> pathlib.Path:
    if org_name:
        app_path = pathlib.Path(INSTALLATION_FOLDER, org_name, app_name).resolve()
        if not app_path.exists():
            raise click.UsageError(f'Install the app "{app_name}" first.')

        return app_path

    organizations = await get_organizations(INSTALLATION_FOLDER)
    if not organizations:
        raise click.exceptions.UsageError(f'Install the app "{app_name}" first.')

    possible_orgs = [
        org
        for org in organizations
        if org.joinpath(app_name).resolve().exists()
    ]
    if not possible_orgs:
        raise click.exceptions.UsageError(f'Install the app "{app_name}" first.')

    if len(possible_orgs) == 1:
        return possible_orgs.pop().joinpath(app_name).resolve()

    click.echo(f'The app "{app_name}" is present in more than one organization.')
    click.echo(f'Which organization you want to use?')
    for i, org in enumerate(organizations):
        click.echo(f'{i + 1}) {org.name}')

    choice = click.prompt('Choose organization number', type=int)
    return possible_orgs[choice - 1].joinpath(app_name).resolve()
