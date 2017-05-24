import telepot
import logging
import json

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class BotAdapter(telepot.Bot):
    def __init__(self, token, buttons=[]):
        super().__init__(token)
        keyboard = {'resize_keyboard': True,
                    'keyboard': BotAdapter.generate_keyboard(buttons)}
        self.commands = {}
        self.default_keyboard = json.dumps(keyboard)

    @staticmethod
    def generate_keyboard(texts, row_len=None):
        """
           Takes a list of strings and returns a matrix of {'text':"stuff"} elements
           Useful for making a keyboard
           default row_len is 2 for less then 9 buttons, 3 otherwise
           ['a','b','c'] --> [[{'text':'a'},{'text':'b'}],[{'text':'c'}]]
        """
        texts = list(texts)
        if row_len is None:
            row_len = 2 if len(texts) < 9 else 3
        text_matrix = [texts[i:i + row_len] for i in range(0, len(texts), row_len)]
        keyboard = [[{'text': text} for text in row] for row in text_matrix]
        return keyboard

    def send(self, chat_id, text, show_keyboard=True, reply_markup=None, **kwargs):
        """
            Equivalent of sendMessage, uses the default keyboard or removes it
        """
        if not show_keyboard:
            reply_markup = json.dumps({'remove_keyboard': True})
        elif reply_markup is None:
            reply_markup = self.default_keyboard
        return self.sendMessage(chat_id, text, reply_markup=reply_markup, **kwargs)

    def add_command(self, command, function):
        if not command.startswith("/"):
            command = '/' + command
        self.commands[command] = function

    def handler(self, message):
        if 'text' not in message:
            self.default_handle(self, message)
            return
        text = message['text']
        if message['chat']['id'] in self.personal_handle:
            self.personal_handle[message['chat']['id']](self, message)
        elif (text.split()[0].split('@')[0] in self.commands): #TODO check for bot name
            command = message['text'].split()[0].split('@')[0]
            logger.info("{} called by {}".format(command, message['from']))
            self.commands[command](self, message)
        else:
            self.default_handle(self, message)

    def start_handling(self, handle=None):
        if handle:
            self.default_handle = handle
        else:
            self.default_handle = lambda bot, message: 1
        self.personal_handle = {} # personal handles for bot.ask
        self.message_loop(callback=self.handler)

    def ask(self, chat_id, question, reply_handler, possible_replies=[]):
        possible_replies = list(possible_replies)
        possible_replies.append('/cancel')
        keyboard = BotAdapter.generate_keyboard(possible_replies)
        reply_markup = json.dumps({'force_reply': True,
                                   'keyboard': keyboard,
                                   'one_time_keyboard': True,
                                   'resize_keyboard': True})
        def temp_handle(bot, message):
            del self.personal_handle[chat_id]  # restore normal handle for chat
            if 'text' in message and message['text'] == '/cancel':
                self.send(chat_id, "Ok.")
            else:
                reply_handler(self, message)
        self.personal_handle[chat_id] = temp_handle
        return self.sendMessage(chat_id, question, reply_markup=reply_markup)
