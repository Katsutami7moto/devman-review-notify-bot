import logging
from textwrap import dedent
from time import sleep, time

import requests
from environs import Env
from telegram import Bot


def send_notification(bot: Bot, chat_id: int, attempt: dict):
    msg = f"""\
    Урок "{attempt.get('lesson_title')}" был проверен!
    {
    'Нужно проработать улучшения!'
    if attempt.get('is_negative')
    else 'Можно приступать к следующему!'
    }
    Ссылка на проверенный урок:
    {attempt.get('lesson_url')}
    """
    bot.send_message(
        chat_id=chat_id,
        text=dedent(msg)
    )


def handle_errors(func_, *args):
    first_reconnection = True
    timestamp = time()
    while True:
        try:
            timestamp = func_(timestamp, *args)

            if not first_reconnection:
                logging.warning('Connection is restored.')
                first_reconnection = True
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


def get_reviews(timestamp: float, bot: Bot, tg_chat_id: int,
                long_poll_url: str, headers: dict) -> float:
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
    elif devman_server_status == 'found':
        timestamp = lessons_reviews.get('last_attempt_timestamp')
        new_attempts = lessons_reviews.get('new_attempts')
        for attempt in new_attempts:
            send_notification(bot, tg_chat_id, attempt)
    else:
        logging.warning(response)
    return timestamp


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

    long_poll_url = 'https://dvmn.org/api/long_polling/'
    headers = {
        'Authorization': f'Token {devman_token}',
    }

    handle_errors(
        get_reviews,
        bot,
        tg_chat_id,
        long_poll_url,
        headers
    )


if __name__ == "__main__":
    main()
