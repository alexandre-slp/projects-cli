import click
from list_command import list_apps_command, Icons


@click.command()
@click.option('-n', '--name', help='Name')
@click.option('-l', '--list', 'list_command', is_flag=True, default=False, help='List apps')
def main(
    name: str,
    list_command: bool,
):
    try:
        if list_command:
            list_apps_command()
            return

        print(name)
    except Exception as exc:
        print(f'Exception: {exc}')
        exit(1)


if __name__ == '__main__':
    main()
