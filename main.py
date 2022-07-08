import json
from time import sleep

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

    first_reconnection = True
    timestamp = 90000000000
    while True:
        try:
            payload = {
                'timestamp': timestamp
            }
            response = requests.get(
                long_poll_url,
                headers=headers,
                params=payload,
                timeout=90
            )
            response.raise_for_status()
            status: dict = response.json()
            print(json.dumps(status, indent=4, ensure_ascii=False))
            timestamp = status['last_attempt_timestamp']
        except requests.exceptions.ConnectionError as connect_err:
            print(f'Connection failure: {connect_err};')
            if first_reconnection:
                print('Retry in 5 seconds')
                sleep(5)
                first_reconnection = False
            else:
                print('Retry in 15 seconds')
                sleep(15)
        except requests.exceptions.ReadTimeout:
            continue
        else:
            first_reconnection = True


if __name__ == "__main__":
    main()
