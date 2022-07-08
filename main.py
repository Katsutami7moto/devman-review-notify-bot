import json

import requests
from environs import Env


def main():
    env = Env()
    env.read_env()
    token: str = env('DEVMAN_TOKEN')
    long_poll_url = 'https://dvmn.org/api/long_polling/'
    headers = {
        'Authorization': f'Token {token}',
    }

    while True:
        try:
            response = requests.get(
                long_poll_url,
                headers=headers,
                timeout=5
            )
            response.raise_for_status()
            status = response.json()
            print(json.dumps(status, indent=4, ensure_ascii=False))
        except requests.exceptions.ReadTimeout:
            continue


if __name__ == "__main__":
    main()
