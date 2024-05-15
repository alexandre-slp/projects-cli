import asyncio
import os
import re


async def get_organizations_from_env() -> set:
    organizations = set()
    pattern = re.compile(r'^GITHUB_(\w+)_TOKEN')
    env_keys = os.environ.keys()
    async with asyncio.TaskGroup() as tg:
        for key in env_keys:
            tg.create_task(get_organization_names(organizations, pattern, key))

    return organizations


async def get_organization_names(orgs: set, match_pattern: re.Pattern, env: str):
    match = re.fullmatch(match_pattern, env)
    if match and match.groups():
        org_name = match.groups()[0].lower()
        orgs.add(org_name)


async def get_org_token(org_name):
    token = os.environ.get(f'GITHUB_{org_name.upper()}_TOKEN')
    return token
