import asyncio
import json

import github
from github import Github, Auth

from env import get_organizations_from_env, get_org_token
from utils import global_options


async def get_organization_apps_on_github(organizations: dict):
    for org in await get_organizations_from_env():
        organizations[org] = dict()

    if not organizations:
        print('No organizations found in environment.')

    async with asyncio.TaskGroup() as tg:
        for org in organizations:
            tg.create_task(get_organization_repos(org, organizations[org]))


async def get_organization_repos(org_name: str, org_apps: dict):
    try:
        token = await get_org_token(org_name)
        gh = Github(auth=Auth.Token(token))
        full_org_repos = gh.get_organization(org_name).get_repos()
        async with asyncio.TaskGroup() as tg:
            for repo in full_org_repos:
                tg.create_task(get_repos_with_instructions(org_apps, repo))

    except Exception as exc:
        if global_options.VERBOSE:
            print(f'Error while getting {org_name} repos: {exc}')


async def get_repos_with_instructions(repos: dict, repo: github.Repository):
    app_name = repo.name.lower()
    repos[app_name] = {
        'installed': False,
        'running': False,
        'instructions': await get_app_instructions(app_name, repo)
    }


async def get_app_instructions(app_name: str, repo: github.Repository):
    try:
        instructions = json.loads(repo.get_contents('.procli.json').decoded_content.decode())
        assert type(instructions['start']) is str
        assert type(instructions['stop']) is str
        return instructions

    except Exception as exc:
        if global_options.LIST_APPS_WITHOUT_INSTRUCTIONS:
            print(f'Missing instructions from {app_name}: {exc}')
