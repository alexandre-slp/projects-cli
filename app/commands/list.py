import asyncio

from app.utils.local import get_organization_apps_locally
from app.utils.network import is_network_ok
from app.utils.printer import show_apps_by_organization, print_legend, start_spinner, stop_spinner
from app.utils.repo import get_organization_apps_on_github


async def list_apps_command(show_captions: bool):
    start_spinner()
    try:
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
            if await is_network_ok():
                tg.create_task(get_organization_apps_on_github(apps_by_organization_on_github))

            tg.create_task(get_organization_apps_locally(apps_by_organization_locally))

        merged_apps_by_organization = await merge_github_and_local_apps(
            apps_by_organization_locally,
            apps_by_organization_on_github
        )
        stop_spinner()
        await show_apps_by_organization(merged_apps_by_organization)
        if show_captions:
            await print_legend()
    except Exception as exc:
        # Just to stop spinner
        stop_spinner()
        raise exc


async def merge_github_and_local_apps(apps_by_organization_locally, apps_by_organization_on_github):
    merged = apps_by_organization_on_github | apps_by_organization_locally
    for org in merged:
        merged[org] = apps_by_organization_on_github.get(org, {}) | apps_by_organization_locally.get(org, {})

    return merged
