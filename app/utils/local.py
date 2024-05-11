import json
from pathlib import Path

import docker


INSTALLATION_FOLDER = Path(Path.home().joinpath('procli'))


async def get_organization_apps_locally(organizations: dict, path=INSTALLATION_FOLDER):
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
