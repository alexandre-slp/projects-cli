import math
from pathlib import Path

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
    not_installed = f'{Style.white}☐{Style.reset}'
    not_installed2 = f'{Style.white}⊘{Style.reset}'
    running = f'{Style.green}☑{Style.reset}'
    running2 = f'{Style.green}✔{Style.reset}'
    stopped = f'{Style.red}☒{Style.reset}'
    stopped2 = f'{Style.red}✖{Style.reset}'


def list_apps_command():
    apps = get_apps()
    formatted_matrix, max_width, num_cols = format_matrix(apps)

    table = texttable.Texttable()
    table.set_chars(['', '', '', ''])
    table.set_cols_width([max_width] * num_cols)
    table.add_rows(formatted_matrix, header=False)

    header_name = 'Apps'
    header_division_char = '='
    header_division = math.floor((max_width + num_cols/2) * 4)
    header_position = math.floor(header_division/2 - len(header_name)/2)
    print(f'{header_position * " "}{header_name}')
    print(header_division * header_division_char)
    print(table.draw())


def get_apps() -> list:
    apps_path_var = ''
    manifests_name = 'manifests'

    apps_path = Path(Path.home().joinpath(apps_path_var))
    if not apps_path.exists():
        raise Exception("Installation path doesn't exists")

    with open(apps_path.joinpath(manifests_name)) as file:
        apps = [f"{line.split('.')[0]}" for line in file]

    apps = [
        {
            'name': app_name,
            'installed': get_app_install_status(app_name),
            'running': get_app_running_status(app_name)
        }
        for app_name in apps
    ]
    return apps


def get_app_install_status(app: str) -> bool:
    pass


def get_app_running_status(app: str) -> bool:
    pass


def format_matrix(apps: list) -> (list, int, int):
    max_num_cols = 4
    apps.sort(key=lambda app: app['name'])
    app_len = len(apps)
    num_cols = app_len if app_len <= max_num_cols else max_num_cols
    num_rows = math.ceil(app_len/num_cols)
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
