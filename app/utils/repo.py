import asyncio
import json

import click
import github
from github import Github, Auth

from app.utils.env import get_organizations_from_env, get_org_token
from app.utils import global_options


async def get_organization_apps_on_github(organizations: dict):
    for org in await get_organizations_from_env():
        organizations[org] = dict()

    if not organizations:
        click.secho('No organizations found in environment.', fg='yellow', bold=True)

    async with asyncio.TaskGroup() as tg:
        for org in organizations:
            tg.create_task(get_organization_apps(org, organizations[org]))


async def get_organization_apps(org_name: str, org_apps: dict):
    try:
        token = await get_org_token(org_name)
        gh = Github(auth=Auth.Token(token))
        full_org_repos = gh.get_organization(org_name).get_repos()
        async with asyncio.TaskGroup() as tg:
            for repo in full_org_repos:
                tg.create_task(get_apps_with_instructions(org_apps, repo))

    except Exception as exc:
        if global_options.VERBOSE:
            click.secho(f'Error while getting {org_name} repos: {exc}', fg='red', bold=True)


async def get_apps_with_instructions(repos: dict, repo: github.Repository):
    app_name = repo.name.lower()
    instructions = await get_app_instructions(app_name, repo)
    if not instructions and not global_options.LIST_APPS_WITHOUT_INSTRUCTIONS:
        return

    repos[app_name] = {
        'installed': False,
        'running': False,
        'instructions': instructions
    }


async def get_app_instructions(app_name: str, repo: github.Repository):
    try:
        return json.loads(repo.get_contents('.procli.json').decoded_content.decode())

    except Exception as exc:
        if global_options.VERBOSE:
            click.secho(f'Missing instructions from {app_name}: {exc}', fg='yellow', bold=True)


async def get_organization_app_url(app_name: str, org_name: str, is_http: bool) -> str:
    token = await get_org_token(org_name)
    gh = Github(auth=Auth.Token(token))
    app_repo = gh.get_organization(org_name).get_repo(app_name)
    if is_http:
        return app_repo.clone_url

    return app_repo.ssh_url
