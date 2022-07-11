import logging
from textwrap import dedent
from time import sleep, time

import requests
from environs import Env
from telegram import Bot


def send_notification(bot: Bot, chat_id: int, attempt: dict):
    msg = f"""\
    Урок "{attempt['lesson_title']}" был проверен!
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
        text=dedent(msg)
    )


def get_reviews(devman_token: str, bot: Bot, tg_chat_id: int):
    long_poll_url = 'https://dvmn.org/api/long_polling/'
    headers = {
        'Authorization': f'Token {devman_token}',
    }
    first_reconnection = True
    timestamp = time()
    while True:
        try:
            payload = {
                'timestamp': timestamp
            }
            response = requests.get(
                long_poll_url,
                headers=headers,
                params=payload,
                timeout=120
            )
            response.raise_for_status()
            lessons_reviews: dict = response.json()
            devman_server_status = lessons_reviews.get('status')

            if devman_server_status == 'timeout':
                timestamp = lessons_reviews.get('timestamp_to_request')
                continue
            elif devman_server_status == 'found':
                timestamp = lessons_reviews['last_attempt_timestamp']
                new_attempts: list[dict] = lessons_reviews['new_attempts']
                for attempt in new_attempts:
                    send_notification(bot, tg_chat_id, attempt)
            else:
                logging.warning(response)
        except requests.exceptions.ConnectionError as connect_err:
            logging.exception(connect_err)
            if first_reconnection:
                logging.warning('Retry in 5 seconds...')
                sleep(5)
                first_reconnection = False
            else:
                logging.warning('Retry in 15 seconds...')
                sleep(15)
        except requests.exceptions.ReadTimeout as err:
            logging.exception(err)
        else:
            if not first_reconnection:
                logging.warning('Connection is restored.')
                first_reconnection = True


def main():
    env = Env()
    env.read_env()
    devman_token: str = env('DEVMAN_TOKEN')
    bot = Bot(token=env('TELEGRAM_BOT_TOKEN'))
    tg_chat_id: int = env.int('TELEGRAM_CHAT_ID')
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    get_reviews(devman_token, bot, tg_chat_id)


if __name__ == "__main__":
    main()
