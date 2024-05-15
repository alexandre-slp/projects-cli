import asyncio
import json
from pathlib import Path

import click
import docker

from utils import global_options

INSTALLATION_FOLDER = Path(Path.home().joinpath('procli').resolve())


async def get_organization_apps_locally(organizations: dict, path=INSTALLATION_FOLDER):
    orgs = await get_organizations(path)
    async with asyncio.TaskGroup() as tg:
        for org in orgs:
            tg.create_task(get_apps_from_org(org, organizations, path))


async def get_organizations(path: Path) -> list[Path]:
    await create_installation_folder(path)
    orgs = [org for org in path.iterdir() if org.is_dir()]
    return orgs


async def get_apps_from_org(org_path: Path, organizations: dict, path: Path):
    async with asyncio.TaskGroup() as tg:
        for app in path.joinpath(org_path).resolve().iterdir():
            tg.create_task(get_app_infos(app, org_path, organizations, path))


async def get_app_infos(app_path: Path, org_path: Path, organizations: dict, path: Path):
    if app_path.is_dir():
        # there are no duplicated orgs nor apps
        org_name = org_path.name.lower()
        app_name = app_path.name.lower()
        organizations[org_name] = {
            app_name: {
                'installed': True,
                'running': await get_app_running_status(app_name),
                'instructions': await get_app_instructions(path.joinpath(org_path).joinpath(app_path).resolve()),
            }
        }


async def create_installation_folder(path: Path):
    if path.exists():
        return

    path.mkdir()


async def get_app_running_status(app_name: str) -> bool:
    try:
        client = docker.from_env()
        container = client.containers.get(app_name)
        if container.status == 'running':
            return True

        return False
    except Exception as exc:
        if global_options.VERBOSE:
            click.echo(f'App not found on docker: {exc}')
        return False


async def get_app_instructions(path: Path) -> str:
    try:
        with open(path.joinpath('.procli.json').resolve()) as f:
            return json.loads(f.read())

    except Exception as exc:
        if global_options.VERBOSE:
            click.echo(f'Failed to load instructions from {path.name}: {exc}')
