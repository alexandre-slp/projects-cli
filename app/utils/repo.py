import asyncio
import json
import os
import re

import github
from github import Github, Auth


async def get_organization_apps_on_github(organizations: dict):
    pattern = re.compile(r'^GITHUB_(\w+)_TOKEN')
    env_keys = os.environ.keys()
    async with asyncio.TaskGroup() as tg:
        for key in env_keys:
            tg.create_task(get_organization_names(organizations, pattern, key))

    if not organizations:
        print('No tokens found. Please confirm env var is in the following format: GITHUB_COMPANY_TOKEN')

    async with asyncio.TaskGroup() as tg:
        for org in organizations:
            tg.create_task(get_organization_repos(org, organizations[org]))


async def get_organization_names(orgs: dict, match_pattern: re.Pattern, env: str):
    match = re.fullmatch(match_pattern, env)
    if match and match.groups():
        org_name = match.groups()[0].lower()
        orgs[org_name] = dict()


async def get_organization_repos(org_name: str, org_apps: dict):
    try:
        token = os.environ.get(f'GITHUB_{org_name.upper()}_TOKEN')
        gh = Github(auth=Auth.Token(token))
        full_org_repos = gh.get_organization(org_name).get_repos()
        async with asyncio.TaskGroup() as tg:
            for repo in full_org_repos:
                tg.create_task(get_repos_with_instructions(org_apps, repo))

    except Exception as exc:
        # TODO: Handle error
        pass


async def get_repos_with_instructions(repos: dict, repo: github.Repository):
    try:
        instructions = json.loads(repo.get_contents('.procli.json').decoded_content.decode())
        app_name = repo.name.lower()
        repos[app_name] = {
            'installed': False,
            'running': False,
            'instructions': instructions
        }

    except Exception as exc:
        # TODO: Handle error
        pass
