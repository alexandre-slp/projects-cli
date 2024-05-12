import asyncio
import math

import texttable


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
    not_installed = f'☐'
    not_installed2 = f'⊘'
    not_installed3 = f'ﰮ'

    running = f'{Style.green}☑{Style.reset}'
    running2 = f'{Style.green}✔{Style.reset}'
    running3 = f'{Style.green}ﲏ{Style.reset}'

    stopped = f'{Style.red}☒{Style.reset}'
    stopped2 = f'{Style.red}✖{Style.reset}'
    stopped3 = f'{Style.red}ﱥ{Style.reset}'


async def show_apps_by_organization(merged_apps_by_organization: dict):
    if not merged_apps_by_organization:
        print('No apps found.')
        return

    for org in merged_apps_by_organization:
        formatted_matrix, max_width, num_cols = await format_matrix(merged_apps_by_organization[org])
        table = texttable.Texttable()
        table.set_chars(['', '', '', ''])
        table.set_cols_width([max_width] * num_cols)
        table.add_rows(formatted_matrix, header=False)
        header_name = f'{Style.bold}{Style.blue}{org.capitalize()}{Style.reset}'
        header_division_char = f'{Style.bold}{Style.yellow}={Style.reset}'
        header_division_length = math.floor((max_width + num_cols / 2) * num_cols)
        header_position = math.floor(header_division_length / 2 - len(header_name) / 2)
        print(f'{" " * header_position}{header_name}')
        print(header_division_char * header_division_length)
        print(table.draw())

    await print_legend()


async def format_matrix(apps: dict) -> (list, int, int):
    max_num_cols = 6
    apps_with_status = await format_app_status(apps)
    app_len = len(apps_with_status)
    num_cols = app_len if app_len <= max_num_cols else max_num_cols
    num_rows = math.ceil(app_len / num_cols)
    formatted_apps = [['' for _ in range(num_cols)] for _ in range(num_rows)]
    max_col_width = 0
    for i in range(app_len):
        app_width = len(apps_with_status[i])
        if app_width > max_col_width:
            max_col_width = app_width

        line = divmod(i, num_rows)[1]
        column = divmod(i, num_rows)[0]
        formatted_apps[line][column] = apps_with_status[i]

    return formatted_apps, max_col_width, num_cols


async def format_app_status(apps: dict) -> list:
    apps_with_status = []
    async with asyncio.TaskGroup() as tg:
        for app in apps.keys():
            tg.create_task(add_icon_and_style(app, apps, apps_with_status))

    apps_with_status.sort()
    return apps_with_status


async def add_icon_and_style(app, apps, apps_with_status):
    styled_app_name = f'{Style.bold}{app}{Style.reset}'
    formatted_app = f'{Icons.not_installed3} {styled_app_name}'
    if apps.get(app).get('running'):
        formatted_app = f'{Icons.running3} {styled_app_name}'

    elif apps.get(app).get('installed'):
        formatted_app = f'{Icons.stopped3} {styled_app_name}'

    apps_with_status.append(formatted_app)


async def print_legend():
    print(f'{Icons.not_installed3} {Style.bold}-> uninstalled{Style.reset}')
    print(f'{Icons.running3} {Style.bold}-> running{Style.reset}')
    print(f'{Icons.stopped3} {Style.bold}-> stopped{Style.reset}')
