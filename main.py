import logging
from collections import namedtuple
from textwrap import dedent
from time import sleep, time

import requests
from environs import Env
from telegram import Bot

Timestamp = namedtuple('Timestamp', 'value')

logger = logging.getLogger('Logger')


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_token, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = Bot(token=tg_token)

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def send_notification(attempt: dict):
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
    logger.info(dedent(msg))


def get_reviews(timestamp: Timestamp, long_poll_url: str, headers: dict):
    payload = {
        'timestamp': timestamp.value
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
        timestamp.value = lessons_reviews.get('timestamp_to_request')
    elif devman_server_status == 'found':
        timestamp.value = lessons_reviews.get('last_attempt_timestamp')
        new_attempts = lessons_reviews.get('new_attempts')
        for attempt in new_attempts:
            send_notification(attempt)
    else:
        logger.error(response)


def handle_errors_getting_reviews(long_poll_url: str, headers: dict):
    first_reconnection = True
    timestamp = Timestamp(time())
    while True:
        try:
            get_reviews(timestamp, long_poll_url, headers)

            if not first_reconnection:
                logger.warning('Connection is restored.')
                first_reconnection = True
        except requests.exceptions.ConnectionError as connect_err:
            if first_reconnection:
                logger.error('Connection is down!')
                logger.exception(connect_err)
                logger.warning('Retry in 5 seconds...')
                sleep(5)
                first_reconnection = False
            else:
                logger.error('Connection is still down!')
                logger.warning('Retry in 15 seconds...')
                sleep(15)
        except requests.exceptions.ReadTimeout as err:
            logger.error('Client read is timeout!')
            logger.exception(err)
        except Exception as other_err:
            logger.error('Bot encountered an error!')
            logger.exception(other_err)


def main():
    env = Env()
    env.read_env()
    devman_token: str = env('DEVMAN_TOKEN')
    tg_token: str = env('TELEGRAM_BOT_TOKEN')
    tg_chat_id: int = env.int('TELEGRAM_CHAT_ID')

    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogsHandler(tg_token, tg_chat_id))
    logger.info('Bot is running.')

    long_poll_url = 'https://dvmn.org/api/long_polling/'
    headers = {
        'Authorization': f'Token {devman_token}',
    }
    handle_errors_getting_reviews(long_poll_url, headers)


if __name__ == "__main__":
    main()
