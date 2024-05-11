import asyncio
import json
import math
import os
import re
from pathlib import Path

import docker
import github
import texttable
from github import Auth
from github import Github

INSTALLATION_FOLDER = Path(Path.home().joinpath('procli'))


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
        tg.create_task(get_organization_apps_locally(INSTALLATION_FOLDER, apps_by_organization_locally))

    merged_apps_by_organization = await merge_apps(apps_by_organization_locally, apps_by_organization_on_github)
    show_apps_by_organization(merged_apps_by_organization)


async def merge_apps(apps_by_organization_locally, apps_by_organization_on_github):
    # TODO: parallelize process
    merged = apps_by_organization_on_github.copy()
    for org in merged:
        github_org_apps = apps_by_organization_on_github.get(org)
        local_org_apps = apps_by_organization_locally.get(org)
        if local_org_apps:
            merged[org] = {**github_org_apps, **local_org_apps}

    return merged


def show_apps_by_organization(merged_apps_by_organization: dict):
    if not merged_apps_by_organization:
        print('No apps found.')
        return

    for org in merged_apps_by_organization:
        formatted_matrix, max_width, num_cols = format_matrix(merged_apps_by_organization[org])
        table = texttable.Texttable()
        table.set_chars(['', '', '', ''])
        table.set_cols_width([max_width] * num_cols)
        table.add_rows(formatted_matrix, header=False)
        header_name = f'{org}'.capitalize()
        header_division_char = '='
        header_division = math.floor((max_width + num_cols / 2) * num_cols)
        header_position = math.floor(header_division / 2 - len(header_name) / 2)
        print(f'{" " * header_position}{header_name}')
        print(header_division * header_division_char)
        print(table.draw())


def format_matrix(apps: dict) -> (list, int, int):
    apps = [app.capitalize() for app in apps.keys()]
    max_num_cols = 6
    apps.sort()
    app_len = len(apps)
    num_cols = app_len if app_len <= max_num_cols else max_num_cols
    num_rows = math.ceil(app_len / num_cols)
    formatted_apps = [['' for _ in range(num_cols)] for _ in range(num_rows)]
    max_col_width = 0
    for i in range(app_len):
        app_width = len(apps[i])
        if app_width > max_col_width:
            max_col_width = app_width
        line = divmod(i, num_rows)[1]
        column = divmod(i, num_rows)[0]
        formatted_apps[line][column] = apps[i]

    return formatted_apps, max_col_width, num_cols


async def get_organization_apps_locally(path: Path, organizations: dict):
    # TODO: parallelize process
    create_installation_folder(path)
    orgs = [org for org in path.iterdir() if org.is_dir()]
    for org in orgs:
        for app in path.joinpath(org).iterdir():
            if app.is_dir():
                # there are no duplicated orgs nor apps
                org_name = org.name.lower()
                app_name = app.name.lower()
                organizations[org_name] = {
                    app_name: {
                        'installed': True,
                        'running': get_app_running_status(app_name),
                        'instructions': get_app_instructions(path.joinpath(org).joinpath(app)),
                    }
                }


def create_installation_folder(path: Path):
    if path.exists():
        return

    path.mkdir()


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


def get_app_running_status(app_name: str) -> bool:
    try:
        client = docker.from_env()
        container = client.containers.get(app_name)
        if container.status == 'running':
            return True

        return False
    except Exception as exc:
        # App not found on docker
        return False


def get_app_instructions(path: Path) -> str:
    try:
        with open(path.joinpath('.procli.json').resolve()) as f:
            return json.loads(f.read())

    except Exception as exc:
        # TODO: Handle error
        pass
