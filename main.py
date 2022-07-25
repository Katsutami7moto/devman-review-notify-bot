import logging
from textwrap import dedent
from time import sleep, time

import requests
from environs import Env
from telegram import Bot


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_token, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = Bot(token=tg_token)

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def send_notification(logger: logging.Logger, attempt: dict):
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


def handle_errors(func_, logger: logging.Logger, *args):
    first_reconnection = True
    timestamp = time()
    while True:
        try:
            timestamp = func_(timestamp, logger, *args)

            if not first_reconnection:
                logger.warning('Connection is restored.')
                first_reconnection = True
        except requests.exceptions.ConnectionError as connect_err:
            logger.error('Connection is down!')
            logger.exception(connect_err)
            if first_reconnection:
                logger.warning('Retry in 5 seconds...')
                sleep(5)
                first_reconnection = False
            else:
                logger.warning('Retry in 15 seconds...')
                sleep(15)
        except requests.exceptions.ReadTimeout as err:
            logger.error('Client read is timeout!')
            logger.exception(err)
        except Exception as other_err:
            logger.error('Bot encountered an error!')
            logger.exception(other_err)


def get_reviews(timestamp: float, logger: logging.Logger,
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
            send_notification(logger, attempt)
    else:
        logger.warning(response)
    return timestamp


def main():
    env = Env()
    env.read_env()
    devman_token: str = env('DEVMAN_TOKEN')
    tg_token: str = env('TELEGRAM_BOT_TOKEN')
    tg_chat_id: int = env.int('TELEGRAM_CHAT_ID')

    logger = logging.getLogger('Logger')
    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogsHandler(tg_token, tg_chat_id))
    logger.info('Bot is running.')

    long_poll_url = 'https://dvmn.org/api/long_polling/'
    headers = {
        'Authorization': f'Token {devman_token}',
    }
    handle_errors(
        get_reviews,
        logger,
        long_poll_url,
        headers
    )


if __name__ == "__main__":
    main()
