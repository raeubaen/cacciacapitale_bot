from django.apps import AppConfig
import sys
import logging
from .bot_config import bot_config
from telegram import Bot as telegramBot
from bot_site.settings import DEBUG


class adminHandler(logging.Handler):
    def __init__(self, token=None, admin_id=None):
        self.bot = telegramBot(token)
        self.admin_id = admin_id
        logging.Handler.__init__(self)

    def emit(self, record):
        with open("log.txt", "w") as out_file:
            out_file.write(self.format(record))
        with open("log.txt", "rb") as in_file:
            self.bot.send_document(self.admin_id, in_file)


class BotConfig(AppConfig):
    name = "Bot"

    def ready(self):
        if not (
            set(sys.argv)
            & set(
                [
                    "makemigrations",
                    "migrate",
                    "collectstatic",
                    "createsuperuser",
                    "shell",
                ]
            )
        ):
            import Bot.bot_thread as bot_thread
            from .models import Bot_Table
            from .exceptions import UniqueObjectError

            Bot_Table.objects.all().delete()
            try:
                Bot_Table.objects.create(**bot_config)
            except UniqueObjectError:
                logging.debug("", exc_info=True)
            bot = Bot_Table.objects.first()
            _hd = adminHandler(token=bot.token, admin_id=bot.admin_id)
            level = logging.ERROR
            _hd.setLevel(level)
            if not DEBUG:
                logging.getLogger("").addHandler(_hd)

            bot_thread.run()
