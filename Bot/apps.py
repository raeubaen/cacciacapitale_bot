from django.apps import AppConfig
import sys
import logging
from .bot_config import bot_config
from .bot_config import admin_ids
from telegram import Bot as telegramBot
from bot_site.settings import DEBUG


class adminHandler(logging.Handler):
    def __init__(self, token=None, admin_ids=None):
        self.bot = telegramBot(token)
        self.admin_ids = admin_ids
        logging.Handler.__init__(self)

    def emit(self, record):
        with open("log.txt", "w") as out_file:
            out_file.write(self.format(record))
        with open("log.txt", "rb") as in_file:
            for id in self.admin_ids:
                self.bot.send_document(id, in_file)


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
                Bot_Table_instance = Bot_Table.objects.create(**bot_config)
                for id in admin_ids:
                    AdminId.objects.create(id=id, bot=Bot_Table_instance)
            except UniqueObjectError:
                logging.debug("", exc_info=True)
            bot = Bot_Table.objects.first()
            _hd = adminHandler(token=bot.token, admin_id=list(bot.adminid_set.values_list()))
            level = logging.ERROR
            _hd.setLevel(level)
            if not DEBUG:
                logging.getLogger("").addHandler(_hd)

            bot_thread.run()
