import asyncio

from app.utils.local import get_organization_apps_locally
from app.utils.printer import show_apps_by_organization

from app.utils.repo import get_organization_apps_on_github


class Style:
    csi = '\x1b['
    reset = '\x1b[0m'
    bold = '\x1b[1m'
    italic = '\x1b[3m'
    underline = '\x1b[4m'
    fontDefault = '\x1b[10m'
    font2 = '\x1b[11m'
    font3 = '\x1b[12m'
    font4 = '\x1b[13m'
    font5 = '\x1b[14m'
    font6 = '\x1b[15m'
    imageNegative = '\x1b[7m'
    imagePositive = '\x1b[27m'
    black = '\x1b[30m'
    red = '\x1b[31m'
    green = '\x1b[32m'
    yellow = '\x1b[33m'
    blue = '\x1b[34m'
    magenta = '\x1b[35m'
    cyan = '\x1b[36m'
    white = '\x1b[37m'
    bg_black = '\x1b[40m'
    bg_red = '\x1b[41m'
    bg_green = '\x1b[42m'
    bg_yellow = '\x1b[43m'
    bg_blue = '\x1b[44m'
    bg_magenta = '\x1b[45m'
    bg_cyan = '\x1b[46m'
    bg_white = '\x1b[47m'


class Icons:
    # unicode characters: https://www.tamasoft.co.jp/en/general-info/unicode.html
    not_installed = f'{Style.white}☐{Style.reset}'
    not_installed2 = f'{Style.white}⊘{Style.reset}'
    not_installed3 = f'{Style.white}ﰮ{Style.reset}'

    running = f'{Style.green}☑{Style.reset}'
    running2 = f'{Style.green}✔{Style.reset}'
    running3 = f'{Style.green}ﲏ{Style.reset}'

    stopped = f'{Style.red}☒{Style.reset}'
    stopped2 = f'{Style.red}✖{Style.reset}'
    stopped3 = f'{Style.red}ﱥ{Style.reset}'


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
    show_apps_by_organization(merged_apps_by_organization)


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


