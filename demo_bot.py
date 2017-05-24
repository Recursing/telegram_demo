import logging
import os
import time

import telegram_adapter
from gulp_reader import get_articles

logger = logging.getLogger(__name__)


def on_ping(bot, update):
    chat_id = update['chat']['id']
    bot.send(chat_id, '/pong')


def ask_me_stuff(bot, update):
    chat_id = update['chat']['id']

    def on_choice(bot, update):
        chat_id = update['chat']['id']
        if 'text' not in update:
            bot.send(chat_id, '???')
        elif update['text'].lower() not in ("telegram", "whatsapp"):
            bot.send(chat_id, 'haha')
        else:
            text = update['text'].lower()
            if text == "telegram":
                bot.send(chat_id, '👍')
            else:
                bot.send(chat_id, '👎')

    bot.ask(chat_id, "Telegram o Whatsapp?",
            reply_handler=on_choice,
            possible_replies=["Telegram", "Whatsapp"])


def on_pong(bot, update):
    chat_id = update['chat']['id']
    bot.send(chat_id, '/ping')


def on_get_articles(bot, update):
    chat_id = update['chat']['id']
    message_text = ""
    for item in get_articles():
        message_text += f"- <a href=\"{item['link']}\">{item['title']}</a>\n"
    bot.send(chat_id, message_text, parse_mode="HTML")


def on_help(bot, update):
    chat_id = update['chat']['id']
    message = ("/ping to ping\n"
               "/pong to pong\n"
               "/get_articles per vedere gli ultimi articoli su gulp.linux.it\n"
               "/fammi_una_domanda per ricevere una domanda")
    bot.send(chat_id, message)


commands = {
    '/ping': on_ping,
    '/pong': on_pong,
    '/get_articles': on_get_articles,
    '/help': on_help,
    '/start': on_help,
    '/fammi_una_domanda': ask_me_stuff
}


def main():
    button_texts = ['/ping', '/get_articles', '/help', '/fammi_una_domanda']
    token = os.environ["TOKEN"]
    bot = telegram_adapter.BotAdapter(token, button_texts)
    for command, function in commands.items():
        bot.add_command(command, function)
    logger.info('Started bot')
    bot.start_handling()


if __name__ == '__main__':
    main()
    while True:
        time.sleep(20)
