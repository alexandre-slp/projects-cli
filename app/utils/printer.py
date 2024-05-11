import math

import texttable


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
