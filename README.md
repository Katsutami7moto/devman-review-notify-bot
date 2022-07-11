# devman-review-notify-bot
Telegram bot for notification of receiving a Devman (dvmn.org) lesson's code review

### How to install

Python3 should be already installed.
Download the [ZIP archive](https://github.com/Katsutami7moto/devman-review-notify-bot/archive/refs/heads/main.zip) of the code and unzip it.
Then open terminal form unzipped directory and use `pip` (or `pip3`, if there is a conflict with Python2) to install dependencies:
```commandline
pip install -r requirements.txt
```
Before you run any of the scripts, you will need to configure environmental variables:

1. Go to the unzipped directory and create a file with the name `.env` (yes, it has only the extension).
It is the file to contain environmental variables that usually store data unique to each user, thus you will need to create your own.
2. Copy and paste this to `.env` file:
```dotenv
DEVMAN_TOKEN='{devman_token}'
TELEGRAM_BOT_TOKEN='{telegram_token}'
TELEGRAM_CHAT_ID={telegram_chat_id}
```
3. Replace `{devman_token}` with your [Devman API](https://dvmn.org/api/docs/) personal token. For that you have to be signed up for [dvmn.org](https://dvmn.org/).
4. Replace `{telegram_token}` with API token for the Telegram bot you have created with the help of [BotFather](https://telegram.me/BotFather). This token will look something like this: `958423683:AAEAtJ5Lde5YYfkjergber`.
5. Replace `{telegram_chat_id}` with the ID number [userinfobot](https://telegram.me/userinfobot) will give you.

### How to use

Start chat with the bot you have created. Then run the script with this command:
```commandline
python3 main.py
```
Bot will send you messages when your lessons are reviewed.

### Project Goals

The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/).
