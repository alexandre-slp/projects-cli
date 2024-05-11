import asyncio

import click

from app.commands.list_command import list_apps_command


@click.command(context_settings={'help_option_names': ['-h', '--help']})
@click.option('-l', '--list', 'list_command', is_flag=True, default=False, help='List apps')
def main(
        list_command: bool,
):
    try:
        if list_command:
            asyncio.run(list_apps_command())

    except Exception as exc:
        print(f'Exception: {exc}')
        exit(1)


if __name__ == '__main__':
    main()
