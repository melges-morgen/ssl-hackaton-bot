import json
import logging

import markdown
from flask import Flask, request, jsonify

from ChatBot import ChatBot
from TelegramBot import AnswerProvider

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

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
chat_bot = ChatBot()
answer_provider = AnswerProvider()
categories_file = "data/categories.json"
with open(categories_file, 'r') as cf:
    categories = json.loads(cf.read())


@app.route('/api/categories')
def questions():
    return jsonify(categories)

@app.route('/api/categories/<filename>')
def question(filename):
    html = markdown.markdown(answer_provider.resolve_answer(filename))
    return html


@app.route('/api/ask', methods=['POST'])
def ask():
    incoming_text = request.get_json()
    answer = chat_bot.ask(incoming_text)
    logging.info("Incoming message: {}, answer message: {}".format(incoming_text, answer))

    return jsonify(answer_provider.resolve_answer(answer))


if __name__ == '__main__':
    app.run(debug=True)
