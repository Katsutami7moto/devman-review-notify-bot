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
        self.tg_bot = tg_bot
        self.chat_id = chat_id

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


def main():
    env = Env()
    env.read_env()
    tg_bot = Bot(token=env('TELEGRAM_BOT_TOKEN'))
    tg_chat_id: int = env.int('TELEGRAM_CHAT_ID')

    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogsHandler(tg_bot, tg_chat_id))
    logger.info('Bot is running.')

    long_poll_url = 'https://dvmn.org/api/long_polling/'
    headers = {'Authorization': f'Token {env("DEVMAN_TOKEN")}'}
    payload = {'timestamp': time()}

    while True:
        try:
            response = requests.get(
                long_poll_url,
                headers=headers,
                params=payload,
                timeout=120
            )
            response.raise_for_status()
            devman_reviews = response.json()

            if devman_reviews['status'] == 'found':
                payload['timestamp'] = devman_reviews['last_attempt_timestamp']
                for attempt in devman_reviews['new_attempts']:
                    send_notification(tg_bot, tg_chat_id, attempt)
            elif devman_reviews['status'] == 'timeout':
                payload['timestamp'] = devman_reviews['timestamp_to_request']
        except requests.exceptions.ConnectionError:
            logger.exception('Connection is down!')
            sleep(15)
        except requests.exceptions.ReadTimeout:
            logger.exception('Client read is timeout!')
        except Exception:
            logger.exception('Bot encountered an error!')


if __name__ == "__main__":
    main()
