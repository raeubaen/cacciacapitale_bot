from telegram import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ConversationHandler, Filters, BaseFilter
from Bot.utils import already_in
from .models import Captain, Hunter, Bot_Table, Queue
from emoji import emojize
import random
from .TeamHandling import create_nodes, handle_queue
from bot_site.settings import DEBUG
from django.db.models import Count
from .utils import info_summary
import logging

class Accept:  # BEFORE ASKING ANY DATA
    def make(self, update, context):
        if already_in(update.message.chat_id):
            update.message.reply_text(
                "Sei giá iscritto. Se hai dubbi, o necessità particolari,"
                " rivolgiti agli organizzatori (visita la sezione Contatti al sito www.cacciacapitale.it)"
            )
            return ConversationHandler.END
        _markup = ReplyKeyboardMarkup([["Si"], ["No"]], one_time_keyboard=True)
        update.message.reply_text(""
            "Benvenuto nel Bot di Iscrizione a Caccia Capitale.\n"
            "La caccia inizierà il 14/03 sera.\n"
            "Sarai guidato nell'inserimento delle informazioni necessarie.\n"
            "Ti preghiamo di fornire dati corretti e veritieri:"
            " l'inserimento di dati falsi rallenterebbe il processo di iscrizione,"
            " fino eventualmente a farti escludere dalla caccia. \nPer essere rimosso dal computo dei"
            " partecipanti o per interrompere la compilazione é sufficiente che tu"
            " scriva /stop. \nFatto ció potrai comunque ricompilare il modulo scrivendo /start.\n"
            "I dati che inserisci verranno inviati in via definitiva ai capitani alle ore 12.00 del 12/03."
            " Per qualsiasi dubbio, recati su www.cacciacapitale.it"
        )
        update.message.reply_text(
            ""
            " Per prima cosa, ti preghiamo di accettare il trattamento dei dati personali [Si/No].\n"
            " Trovi la nostra privacy policy all'indirizzo www.cacciacapitale.it/privacypolicy.txt",
            reply_markup=_markup,
        )
        return self.num

    def process(self, update, context):
        if update.message.text == "No":
            update.message.reply_text(
                "Per poterti iscrivere alla caccia, è necessario accettare il "
                "trattamento dei dati..\n Se desideri ricominciare la compilazione digita /start"
            )
            return ConversationHandler.END
        return self.make_new(update, context)

    class Filter(BaseFilter):
        def filter(self, message):
            try:
                txt = message.text
                return txt in ("Si", "No")
            except AttributeError:
                return False

    filter = Filter()
    key_verbose_name = "Telegram Chat ID"
    key_name = "id"

class Phone:
    def make(self, update, context):
        em1 = emojize(":telephone:", use_aliases=True)
        em2 = emojize(":mobile_phone:", use_aliases=True)
        _contact_button = KeyboardButton(
            text=em1 + " Invia il tuo numero di telefono " + em2, request_contact=True
        )
        _markup = ReplyKeyboardMarkup([[_contact_button]], one_time_keyboard=True)
        update.message.reply_text(
            text="Necessitiamo del tuo numero di telefono"
            " per poterti eventualmente contattare prima e durante la caccia."
            " Clicca sul bottone in basso",
            reply_markup=_markup,
        )
        return self.num

    def process(self, update, context):
        chat_id = update.message.chat_id
        Hunter.objects.create(id=chat_id, phone=update.message.contact.phone_number)
        return self.make_new(update, context)

    filter = Filters.contact
    key_verbose_name = "Numero di Telefono"
    key_name = "phone"

class Name:
    def make(self, update, context):
        update.message.reply_text("Inserisci il tuo nome (es. Enrico)")
        return self.num

    def process(self, update, context):
        hunter = Hunter.objects.get(id=update.message.chat_id)
        hunter.name = update.message.text
        hunter.save()
        return self.make_new(update, context)

    class Filter(BaseFilter):
        def filter(self, message):
            try:
                txt = message.text
                return all(x.isalpha() or x.isspace() or x == "'" for x in txt)
            except:
                return False

    filter = Filter()
    key_verbose_name = "Nome"
    key_name = "name"

class Surname:
    def make(self, update, context):
        update.message.reply_text("Inserisci il tuo cognome (es. Berlinguer)")
        return self.num

    def process(self, update, context):
        hunter = Hunter.objects.get(id=update.message.chat_id)
        hunter.surname = update.message.text
        hunter.save()
        return self.make_new(update, context)

    filter = Name.filter
    key_verbose_name = "Cognome"
    key_name = "surname"


class Age:
    def make(self, update, context):
        update.message.reply_text("Quanti anni hai? Es. 20")
        return self.num

    def process(self, update, context):
        hunter = Hunter.objects.get(id=update.message.chat_id)
        hunter.age = int(update.message.text)
        hunter.save()
        return self.make_new(update, context)

    class Filter(BaseFilter):
        def filter(self, message):
            try:
                txt = message.text
                return (txt.isdigit()) and 16 < int(txt) < 40
            except AttributeError:
                return False

    filter = Filter()
    key_verbose_name = "Età"
    key_name = "age"


class Uni:
    def make(self, update, context):
        update.message.reply_text(
            "Frequenti l'università? Se sì, indica facoltà, ateneo ed anno di corso. "
            "Es. Fisica alla Sapienza, primo anno"
        )
        return self.num

    def process(self, update, context):
        hunter = Hunter.objects.get(id=update.message.chat_id)
        hunter.uni = update.message.text
        hunter.save()
        return self.make_new(update, context)

    class Filter(BaseFilter):
        def filter(self, message):
            try:
                txt = message.text
                return True
            except AttributeError:
                return False

    filter = Filter()
    key_verbose_name = "Università"
    key_name = "uni"


class Time:
    def make(self, update, context):
        update.message.reply_text(
            "Indica orientativamente da che ora a che ora sarai presente. "
            " La caccia inizierà non prima delle 20.30 e terminerà non oltre le 8.30."
        )
        return self.num

    def process(self, update, context):
        hunter = Hunter.objects.get(id=update.message.chat_id)
        hunter.tframe = update.message.text
        hunter.save()
        return self.make_new(update, context)

    filter = Uni.filter
    key_verbose_name = "Tempistica"
    key_name = "tframe"

class Perc:
    def make(self, update, context):
        update.message.reply_text(
            "In che percentuale conti di poter partecipare alla caccia? Es. 99\n"
            "Se tale percentuale si modifica di molto (sia in positivo che in negativo) avvisa il Comitato"
        )
        return self.num

    def process(self, update, context):
        hunter = Hunter.objects.get(id=update.message.chat_id)
        hunter.perc = int(update.message.text)
        hunter.save()
        return self.make_new(update, context)

    class Filter(BaseFilter):
        def filter(self, message):
            try:
                txt = message.text
                return txt.isdigit() and 1 <= int(txt) <= 100
            except AttributeError:
                return False

    filter = Filter()
    key_verbose_name = "Probabilità di presenza (%)"
    key_name = "perc"


# Handling the process of assigning a captain
class Grouping:  # others questions are in personalQuestions.py
    def make(self, update, context):
        MAX_MEMBERS_PER_TEAM = Bot_Table.objects.first().max_team_size
        cap_q_set = Captain.objects.annotate(num_h=Count('hunter')).filter(num_h__lte=MAX_MEMBERS_PER_TEAM).values_list("anagraphic")
        BUTTONS = [[tpl[0]] for tpl in cap_q_set]
        random.shuffle(BUTTONS)
        BUTTONS.insert(0, ["Crea la tua squadra"])
        _markup = ReplyKeyboardMarkup(BUTTONS, one_time_keyboard=True)
        update.message.reply_text("Scegli il tuo Capitano", reply_markup=_markup)
        return self.num

    def process(self, update, context):
        choice = update.message.text
        hunter = Hunter.objects.get(id=update.message.chat_id)
        if choice == "Crea la tua squadra":
            update.message.reply_text(
                "Contatta il comitato, ti saranno date istruzioni in merito. "
                "Se invece vuoi inserirti in una squadra già presente, clicca /stop, poi /start e ricomincia."
            )
            Queue.objects.create(situation="Richiesta creazione propria squadra", hunter=hunter)
            hunter.save()
            return self.make_new(update, context)
        cap_anag = choice
        queue = Queue.objects.create(situation="In attesa", hunter=hunter)
        hunter.save()
        create_nodes(cap_anag, queue)
        handle_queue(hunter, context)
        return self.make_new(update, context)

    class Filter(BaseFilter):
        def filter(self, message):
            try:
                txt = message.text
                MAX_MEMBERS_PER_TEAM = Bot_Table.objects.first().max_team_size
                cap_q_set = Captain.objects.annotate(num_h=Count('hunter')).filter(num_h__lte=MAX_MEMBERS_PER_TEAM).values_list("anagraphic")
                flat_buttons = [i[0] for i in cap_q_set]
                print(flat_buttons)
                flat_buttons.insert(0, "Crea la tua squadra")
                return txt in flat_buttons
            except AttributeError:
                return False

    filter = Filter()
    key_verbose_name = "Status dell'iscrizione"
    key_name = "queue"


# what happens when conversation_handler.END is triggered
def end_conversation(update, context):
    admin_id = Bot_Table.objects.first().admin_id
    if DEBUG:
        context.bot.send_message(
            chat_id=admin_id,
            text=f"Nuovo iscritto:\n{info_summary(chat_id=update.message.chat_id)}",
        )
    update.message.reply_text(
        "Tutto perfetto, richiesta di iscrizione effettuata!\nTi terremo aggiornato/a. Grazie e a presto!"
    )
    return ConversationHandler.END


# callback for /stop command
def cancel(update, context):
    try:
      hunter = Hunter.objects.get(id=update.message.chat_id)
      hunter.delete()
    except Hunter.DoesNotExist:
      logging.debug("", exc_info=True)
    update.message.reply_text(
        "Tutti i tuoi dati sono stati rimossi; per ricominciare premi /start"
    )
    return ConversationHandler.END


# question_list = [Phone, Grouping]
question_list = [Phone, Name, Surname, Age, Uni, Time, Perc, Grouping]
question_list.insert(0, Accept)
