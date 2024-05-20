import asyncio
import itertools
import math
import os
import re
import threading
import time

import click
import texttable

STOP_EVENT = threading.Event()
SPINNER_THREAD = threading.Thread()


class Icons:
    # unicode characters: https://www.tamasoft.co.jp/en/general-info/unicode.html
    not_installed = click.style('☐')
    not_installed2 = click.style('⊘')
    not_installed3 = click.style('ﰮ')

    running = click.style('☑', fg='green')
    running2 = click.style('✔', fg='green')
    running3 = click.style('ﲏ', fg='green')

    stopped = click.style('☒', fg='red')
    stopped2 = click.style('✖', fg='red')
    stopped3 = click.style('ﱥ', fg='red')


async def show_apps_by_organization(merged_apps_by_organization: dict):
    if not merged_apps_by_organization:
        click.secho('No apps found.', fg='yellow', bold=True)
        return

    organizations = []
    async with asyncio.TaskGroup() as tg:
        for org in merged_apps_by_organization:
            tg.create_task(create_org_apps_table(merged_apps_by_organization, org, organizations))

    organizations.sort(key=lambda x: x['header'])
    for org in organizations:
        click.secho(org['header'], fg='blue', bold=True)
        click.secho(org['division'], fg='yellow', bold=True)
        click.echo(org['apps'].draw())


async def create_org_apps_table(merged_apps_by_organization: dict, org: str, organizations: [dict]):
    formatted_matrix, max_cols_width, max_visible_width, num_cols = await format_matrix(
        merged_apps_by_organization[org])
    table = texttable.Texttable()
    table.set_chars(['', '', '', ''])
    table.set_cols_width([max_cols_width] * num_cols)
    table.add_rows(formatted_matrix, header=False)
    header_name = org.capitalize()
    header_division_length = math.floor((max_visible_width + num_cols / 2) * num_cols)
    header_position = math.floor(header_division_length / 2 - len(header_name) / 2)
    organizations.append({
        'header': f'{" " * header_position}{header_name}',
        'division': '=' * header_division_length,
        'apps': table
    })


async def format_matrix(apps: dict) -> (list, int, int, int):
    word_pattern = re.compile(r'.*m(\w+).*')
    apps_with_status = await format_app_status(apps, word_pattern)
    app_names_width = []
    app_names_visible_width = []

    async with asyncio.TaskGroup() as tg:
        for app_name in apps_with_status:
            tg.create_task(get_app_name_width(app_name, word_pattern, app_names_width, app_names_visible_width))

    max_col_width = max(app_names_width)
    max_col_visible_width = max(app_names_visible_width)
    size = os.get_terminal_size()
    max_num_cols = size.columns // max_col_width
    app_quantity = len(apps_with_status)
    num_cols = app_quantity if app_quantity <= max_num_cols else max_num_cols
    num_rows = math.ceil(app_quantity / num_cols)
    formatted_apps_in_position = [['' for _ in range(num_cols)] for _ in range(num_rows)]

    async with asyncio.TaskGroup() as tg:
        for i, app_name in enumerate(apps_with_status):
            tg.create_task(set_app_position(app_name, formatted_apps_in_position, i, num_rows))

    return formatted_apps_in_position, max_col_width, max_col_visible_width, num_cols


async def get_app_name_width(app_name: str, word_pattern: re.Pattern, app_names_width: [int],
                             app_names_visible_width: [int]):
    app_names_width.append(len(app_name))
    app_names_visible_width.append(len(re.fullmatch(word_pattern, app_name).group(1)))


async def set_app_position(app_name: str, formatted_apps_in_position: [[str]], i: int, num_rows: int):
    line = i % num_rows
    column = i // num_rows
    formatted_apps_in_position[line][column] = app_name


async def format_app_status(apps: dict, word_patter: re.Pattern) -> list:
    apps_with_status = []
    async with asyncio.TaskGroup() as tg:
        for app in apps.keys():
            tg.create_task(add_icon_and_style(app, apps, apps_with_status))

    apps_with_status.sort(key=lambda x: re.fullmatch(word_patter, x).group(1))
    return apps_with_status


async def add_icon_and_style(app, apps, apps_with_status):
    formatted_app = f'{Icons.not_installed3} {click.style(app, bold=True)}'
    if apps.get(app).get('running'):
        formatted_app = f'{Icons.running3} {click.style(app, bold=True)}'

    elif apps.get(app).get('installed'):
        formatted_app = f'{Icons.stopped3} {click.style(app, bold=True)}'

    apps_with_status.append(formatted_app)


async def print_legend():
    click.echo(f'{Icons.not_installed3} {click.style("-> uninstalled", bold=True)}')
    click.echo(f'{Icons.running3} {click.style("-> running", bold=True)}')
    click.echo(f'{Icons.stopped3} {click.style("-> stopped", bold=True)}')


def spinner(stop_event):
    spinner_cycle = itertools.cycle(['|', '/', '—', '\\'])
    while not stop_event.is_set():
        click.secho(next(spinner_cycle), fg='yellow', nl=False)
        time.sleep(0.1)
        click.echo('\b', nl=False)


def start_spinner():
    global STOP_EVENT, SPINNER_THREAD
    STOP_EVENT = threading.Event()
    SPINNER_THREAD = threading.Thread(target=spinner, args=(STOP_EVENT,))
    SPINNER_THREAD.start()


def stop_spinner():
    global STOP_EVENT, SPINNER_THREAD
    STOP_EVENT.set()
    SPINNER_THREAD.join()
