import os
import subprocess
import sys

import telebot
from dotenv import load_dotenv

load_dotenv()

TGBOT_TOKEN = os.getenv('TGBOT_TOKEN')


class Handler(telebot.ExceptionHandler):
    def handle(self, exception):
        if isinstance(exception, telebot.apihelper.ApiTelegramException) and exception.error_code == 409:
            print('Bot is already running. Exiting...')
            os.kill(os.getpid(), 9)
        return True


bot = None if not TGBOT_TOKEN else telebot.TeleBot(TGBOT_TOKEN, exception_handler=Handler())


def check_bot(func):
    def wrapper(*args, **kwargs):
        if not bot:
            return None
        return func(*args, **kwargs)

    return wrapper


def callfunc(func, *args, fail_silently=False, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if not fail_silently:
            raise
        print(f'${func.__module__}.{func.__name__} ({args}) Exception: {e}')

    return None


if __name__ == '__main__' and bot:
    print('Bot running... __main__')
    @bot.message_handler(commands=['start'])
    def start(message: telebot.types.Message):
        print(message.chat.id)
        bot.send_message(message.chat.id, 'Hello!')

    bot.infinity_polling()
elif not bot:
    print('Bot is not defined. Exiting...')
else:
    print('Bot running...')
    print([sys.executable, os.path.join(os.path.dirname(__file__), 'bot.py')])
    proc = subprocess.Popen(
        [sys.executable, os.path.join(os.path.dirname(__file__), 'bot.py')],
        shell=True,
        stdin=None,
        stdout=None,
        stderr=None,
        close_fds=True,
    )
    print(proc.stdout)
    print(proc.stderr)
