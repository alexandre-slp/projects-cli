import asyncio

from app.utils.local import get_organization_apps_locally
from app.utils.printer import show_apps_by_organization

from app.utils.repo import get_organization_apps_on_github


async def list_apps_command():
    apps_by_organization_on_github = dict()
    # Dict struct example:
    # organizations = {
    #     org_name: {
    #         app_name: {
    #             instructions: dict
    #         }
    #     }
    # }
    apps_by_organization_locally = dict()
    # Dict struct example:
    # organizations = {
    #     org_name: {
    #         app_name: {
    #             installed: bool,
    #             running: bool,
    #             instructions: dict
    #         }
    #     }
    # }
    async with asyncio.TaskGroup() as tg:
        tg.create_task(get_organization_apps_on_github(apps_by_organization_on_github))
        tg.create_task(get_organization_apps_locally(apps_by_organization_locally))

    merged_apps_by_organization = await merge_apps(apps_by_organization_locally, apps_by_organization_on_github)
    await show_apps_by_organization(merged_apps_by_organization)


async def merge_apps(apps_by_organization_locally, apps_by_organization_on_github):
    merged = apps_by_organization_on_github.copy()
    async with asyncio.TaskGroup() as tg:
        for org in merged:
            tg.create_task(method_name(apps_by_organization_locally, apps_by_organization_on_github, merged, org))

    return merged


async def method_name(apps_by_organization_locally: dict, apps_by_organization_on_github: dict, merged: dict, org: str):
    github_org_apps = apps_by_organization_on_github.get(org)
    local_org_apps = apps_by_organization_locally.get(org)
    if local_org_apps:
        merged[org] = {**github_org_apps, **local_org_apps}


