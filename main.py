from time import sleep

import requests
from environs import Env
from telegram import Bot


def send_notification(bot: Bot, chat_id: int, attempt: dict):
    msg = f"""Урок "{attempt['lesson_title']}" был проверен!
{
    'Нужно проработать улучшения!'
    if attempt['is_negative']
    else 'Можно приступать к следующему!'
}
Ссылка на проверенный урок:
{attempt['lesson_url']}
"""
    bot.send_message(
        chat_id=chat_id,
        text=msg
    )


def main():
    env = Env()
    env.read_env()
    devman_token: str = env('DEVMAN_TOKEN')
    long_poll_url = 'https://dvmn.org/api/long_polling/'
    headers = {
        'Authorization': f'Token {devman_token}',
    }

    tg_bot_token: str = env('TELEGRAM_BOT_TOKEN')
    bot = Bot(token=tg_bot_token)
    tg_chat_id: int = env.int('TELEGRAM_CHAT_ID')

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
            devman_server_status: dict = response.json()
            timestamp = devman_server_status['last_attempt_timestamp']
            new_attempts: list[dict] = devman_server_status['new_attempts']
            for attempt in new_attempts:
                send_notification(bot, tg_chat_id, attempt)
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
            if not first_reconnection:
                print('Connection is restored.')
                first_reconnection = True


if __name__ == "__main__":
    main()
