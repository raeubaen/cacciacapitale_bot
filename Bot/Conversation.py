from telegram.ext import MessageHandler, Filters, ConversationHandler, CommandHandler
from .Questions import Accept, Phone, Name, Surname, Age, Uni, Time, Perc, Grouping
from .models import Key, Hunter, Bot
from bot_site.settings import DEBUG
from .utils import info_summary


#what happens when conversation_handler.END is triggered
def end_conversation(update, context):
    admin_id = Bot.objects.first().admin_id
    if DEBUG:
      context.bot.send_message(
        chat_id=admin_id,
        text=f"Nuovo iscritto:\n{info_summary(chat_id=update.message.chat_id)}")
    update.message.reply_text("Tutto perfetto, richiesta di iscrizione effettuata!\nTi terremo aggiornato/a. Grazie e a presto!")
    return ConversationHandler.END


#callback for /stop command
def cancel(update, context):
    hunter = Hunter.objects.get(id=update.message.chat_id)
    hunter.delete()
    update.message.reply_text("Tutti i tuoi dati sono stati rimossi; per ricominciare premi /start")
    return ConversationHandler.END


def istances(classes_list):  # makes the conv handler work - connects make, process and new questions
    ist = [cls() for cls in classes_list]
    for i in range(len(ist)):
        ist[i].num = i
        try:
            ist[i].make_new = ist[i + 1].make
        except IndexError:
            ist[i].make_new = end_conversation
    return ist


def states(istances):  # sets the Conversational Handler
    stg = {}
    for ist in istances:
        stg[ist.num] = [
            MessageHandler(ist.filter, ist.process),
            CommandHandler("stop", cancel),
            MessageHandler(~ist.filter, ist.make),
        ]
    return stg


def create_key_list(ist_list):  # gives back a list of keys contained in classes
    key_list = []
    for ist in ist_list:
        try:
            key_list.append(ist.key)
        except AttributeError:
            logging.debug("", exc_info=True)
    return key_list


classes_list = [Phone, Name, Surname, Age, Uni, Time, Perc, Grouping]
classes_list.insert(0, Accept)
ist = istances(classes_list)

key_list = create_key_list(ist)

for key in key_list:
    Key.objects.get_or_create(key=key)


conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", ist[0].make)],
    states=states(ist),
    fallbacks=[CommandHandler("stop", cancel)],
)
