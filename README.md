# devman-review-notify-bot
Telegram bot for notification of receiving a Devman (dvmn.org) lesson's code review

### How to install

Python3 should be already installed.
Download the [ZIP archive](https://github.com/Katsutami7moto/devman-review-notify-bot/archive/refs/heads/main.zip) of the code and unzip it.
Then open terminal form unzipped directory and use `pip` (or `pip3`, if there is a conflict with Python2) to install dependencies:
```commandline
pip install -r requirements.txt
```
Before you run any of the scripts, you will need to configure environment variables:

1. Go to the unzipped directory and create a file with the name `.env` (yes, it has only the extension).
This file will contain environment variables that usually store data unique to each user, thus you will need to create your own.
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

### How to deploy

1. Fork this repository.
2. Sign up at [Heroku](https://id.heroku.com/login).
3. Create [an app](https://dashboard.heroku.com/new-app) at Heroku; choose `Europe` region.
4. [Connect](https://dashboard.heroku.com/apps/devman-review-notify-bot/deploy/github) forked GitHub repository.
5. Go to [Settings](https://dashboard.heroku.com/apps/devman-review-notify-bot/settings) and set `Config Vars` from previously described environment variables, putting each name to `KEY` and value to `VALUE`, e.g. `DEVMAN_TOKEN` to `KEY` and `{devman_token}` (here without `' '` quatation marks) to `VALUE`.
6. Go to [Deploy](https://dashboard.heroku.com/apps/devman-review-notify-bot/deploy/github) section, scroll to bottom, to `Manual Deploy`, be sure to choose `main` branch and click `Deploy Branch` button.
7. Bot should start working and send you a `Bot is running.` message (if you have started the chat with it), but just in case check the [logs](https://dashboard.heroku.com/apps/devman-review-notify-bot/logs) of the app. At the end it should look something like this:
```
2022-07-25T12:52:42.000000+00:00 app[api]: Build succeeded
2022-07-25T12:52:42.153483+00:00 heroku[bot.1]: Stopping all processes with SIGTERM
2022-07-25T12:52:42.338522+00:00 heroku[bot.1]: Process exited with status 143
2022-07-25T12:52:42.793206+00:00 heroku[bot.1]: Starting process with command `python3 main.py`
2022-07-25T12:52:43.389877+00:00 heroku[bot.1]: State changed from starting to up
```

### Project Goals

The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/).
