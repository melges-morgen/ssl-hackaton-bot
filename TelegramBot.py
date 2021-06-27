import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, CallbackQueryHandler
from telegram.ext import CommandHandler
import json

from ChatBot import ChatBot


class AnswerProvider:
    def __init__(self, answers_path="data/answers", categories_file="data/categories.json"):
        with open(categories_file, 'r') as cf:
            self._categories = json.loads(cf.read())
        self._answers_path = answers_path
        self._answers_cache = {}

    def resolve_answer(self, file_name):
        if file_name not in self._answers_cache:
            with open(self._answers_path + '/' + file_name, 'r') as fp:
                self._answers_cache[file_name] = fp.read()
        return self._answers_cache[file_name]

    def categories(self):
        return self._categories


def buttons_for_category(category):
    category_buttons = []
    for file in category["files"]:
        category_buttons.append(InlineKeyboardButton(text=file, callback_data=file))
    return category_buttons


class TelegramBot:
    def __init__(self, telegram_token, chat_bot=ChatBot(), answer_provider=AnswerProvider()):
        self._chat_bot = chat_bot
        self._answer_provider = answer_provider
        self._updater = Updater(token=telegram_token)
        self._dispatcher = self._updater.dispatcher
        self._init_handlers()
        self._updater.start_polling()

    def _init_handlers(self):
        start_handler = CommandHandler('start', lambda update, context: self.start(update, context))
        self._dispatcher.add_handler(start_handler)
        raw_message_handler = MessageHandler(
            Filters.text & (~Filters.command),
            lambda update, context: self.raw_message(update, context)
        )
        self._dispatcher.add_handler(raw_message_handler)
        help_me_handler = CallbackQueryHandler(lambda update, context: self.help_me(update, context),
                                               pattern="alert_help")
        self._dispatcher.add_handler(help_me_handler)
        restart_handler = CallbackQueryHandler(lambda update, context: self.restart(update, context), pattern="restart")
        self._dispatcher.add_handler(restart_handler)
        category_handler = CallbackQueryHandler(lambda update, context: self.category(update, context),
                                                pattern="cat-.*")
        self._dispatcher.add_handler(category_handler)
        file_handler = CallbackQueryHandler(lambda update, context: self.exact_file(update, context),
                                            pattern=".*\\.md")
        self._dispatcher.add_handler(file_handler)

    def help_me(self, update, context):
        logging.info("Help me: " + update.effective_user.username)
        context.bot.answer_callback_query(update.callback_query.id, text="Мы получили ваш запрос")

    @staticmethod
    def restart_button():
        return InlineKeyboardButton(text='Назад', callback_data="restart")

    @staticmethod
    def help_me_button():
        return InlineKeyboardButton(text='Срочно нужна помощь', callback_data="alert_help")

    def start(self, update, context):
        category_buttons = self.category_buttons()
        buttons = [[self.help_me_button()]]
        for category_button in category_buttons:
            buttons.append([category_button])
        buttons.append([self.restart_button()])
        markup = InlineKeyboardMarkup(buttons)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=self._answer_provider.resolve_answer("приветствие.md"),
            reply_markup=markup
        )

    def restart(self, update, context):
        category_buttons = self.category_buttons()
        buttons = [[self.help_me_button()]]
        for category_button in category_buttons:
            buttons.append([category_button])
        buttons.append([self.restart_button()])
        markup = InlineKeyboardMarkup(buttons)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=self._answer_provider.resolve_answer("приветствие_кратко.md"),
            reply_markup=markup
        )
        if update.callback_query is not None:
            context.bot.answer_callback_query(update.callback_query.id)

    def category_buttons(self):
        category_buttons = []
        for category in self._answer_provider.categories():
            category_buttons.append(InlineKeyboardButton(text=category, callback_data="cat-" +
                                                                                      self._answer_provider.categories()[
                                                                                          category]["id"]))
        return category_buttons

    def raw_message(self, update, context):
        incoming_text = update.message.text
        answer = self._chat_bot.ask(incoming_text)
        logging.info("Incoming message: {}, answer message: {}".format(incoming_text, answer))
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=self._answer_provider.resolve_answer(answer),
            parse_mode="Markdown"
        )
        self.restart(update, context)

    def category(self, update, context):
        context.bot.answer_callback_query(update.callback_query.id)
        category_id = update.callback_query.data.replace("cat-", "")
        category = self.find_category(category_id)
        category_buttons = buttons_for_category(self._answer_provider.categories()[category])
        buttons = [[self.help_me_button()]]
        for category_button in category_buttons:
            buttons.append([category_button])
        buttons.append([self.restart_button()])
        markup = InlineKeyboardMarkup(buttons)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Вот что мы нашли",
            reply_markup=markup
        )

    def find_category(self, category_id):
        for category in self._answer_provider.categories():
            if self._answer_provider.categories()[category]["id"] == category_id:
                return category

    def exact_file(self, update, context):
        context.bot.answer_callback_query(update.callback_query.id)
        file = update.callback_query.data
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=self._answer_provider.resolve_answer(file),
            parse_mode="Markdown"
        )
        self.restart(update, context)
