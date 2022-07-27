import logging
from textwrap import dedent
from time import sleep, time

import requests
from environs import Env
from telegram import Bot

logger = logging.getLogger('Logger')


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot: Bot, chat_id: int):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def send_notification(tg_bot: Bot, chat_id: int, attempt: dict):
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
    tg_bot.send_message(chat_id=chat_id, text=dedent(msg))


def fetch_devman_reviews(long_poll_url: str, headers: dict, payload: dict):
    first_reconnection = True
    while True:
        try:
            response = requests.get(long_poll_url, headers=headers,
                                    params=payload, timeout=120)
            response.raise_for_status()
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
        else:
            yield response.json()


def get_timestamp(devman_response: dict):
    devman_response_status = devman_response.get('status')
    if devman_response_status == 'timeout':
        return devman_response.get('timestamp_to_request')
    elif devman_response_status == 'found':
        return devman_response.get('last_attempt_timestamp')
    else:
        logger.error('Devman server response has no status!')
        logger.error(devman_response)


def main():
    env = Env()
    env.read_env()
    devman_token: str = env('DEVMAN_TOKEN')
    tg_token: str = env('TELEGRAM_BOT_TOKEN')
    tg_chat_id: int = env.int('TELEGRAM_CHAT_ID')
    tg_bot = Bot(token=tg_token)

    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogsHandler(tg_bot, tg_chat_id))
    logger.info('Bot is running.')

    long_poll_url = 'https://dvmn.org/api/long_polling/'
    headers = {'Authorization': f'Token {devman_token}'}
    payload = {'timestamp': time()}
    for devman_review in fetch_devman_reviews(long_poll_url, headers, payload):
        timestamp = get_timestamp(devman_review)
        if not timestamp:
            continue
        payload['timestamp'] = timestamp
        if devman_review.get('status') == 'found':
            new_attempts = devman_review.get('new_attempts')
        else:
            continue
        for attempt in new_attempts:
            send_notification(tg_bot, tg_chat_id, attempt)


if __name__ == "__main__":
    main()
