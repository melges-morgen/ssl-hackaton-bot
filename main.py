# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import json
import logging
import nltk

from TelegramBot import TelegramBot

if __name__ == '__main__':
    nltk.download('stopwords')
    logging.basicConfig(
        filename="chat-bot.log",
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logFormatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    rootLogger = logging.getLogger()

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

    with open("config/telegram-config.json", "r") as telegram_config_file:
        telegram_config = json.loads(telegram_config_file.read())
    TelegramBot(telegram_config["token"])

