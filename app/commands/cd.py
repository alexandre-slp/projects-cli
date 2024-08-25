import subprocess

from app.utils.local import get_app_path_interactively


async def cd_app_command(app_name: str, org_name: str):
    app_path = await get_app_path_interactively(app_name, org_name)
    subprocess.run(f'cd {app_path}', shell=True, check=True)
