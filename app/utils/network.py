import requests


async def is_network_ok() -> bool:
    url = "http://www.google.com"
    timeout = 1
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            return True

        return False
    except Exception as exc:
        print(exc)
        return False
