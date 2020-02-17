from telegram import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (ConversationHandler, Filters, BaseFilter)
from Bot.utils import already_in
from .models import Captain, Hunter, Bot_Table, Queue
from emoji import emojize
import random
from .utils import cap_anag_list
from .TeamHandling import create_nodes, handle_queue

class Accept:  # BEFORE ASKING ANY DATA
    def make(self, update, context):
        if already_in(update.message.chat_id):
            update.message.reply_text(
                "Sei giá iscritto. Se hai dubbi, o necessità particolari,"
                " rivolgiti agli organizzatori (visita la sezione Contatti al sito www.cacciacapitale.it)"
            )
            return ConversationHandler.END
        _markup = ReplyKeyboardMarkup([["Si"], ["No"]], one_time_keyboard=True)
        update.message.reply_text("Iscrizioni non attive - per favore non proseguire")
        '''
            "Benvenuto nel Bot di Iscrizione a Caccia Capitale.\n"
            " Qui sarai guidato nella compilazione dei campi richiesti.\n"
            "Ti preghiamo di inserire informazioni corrette e veritiere:"
            " l'inserimento di dati palesemente falsi rallenterebbe il processo di iscrizione,"
            " fino eventualmente a farti escludere dalla Caccia. \nPer essere rimosso dal computo dei"
            " partecipanti o per interrompere la compilazione é sufficiente che tu"
            " scriva /stop. \nFatto ció potrai comunque ricompilare il modulo scrivendo /start.\n"
            "I dati che inserisci verranno inviati in via definitiva ai capitani alle ore 12.00 del 19/12."
            " Per qualsiasi dubbio, recati su https://cacciacapitale.it"
        '''
        update.message.reply_text(
            ""
            " Per prima cosa, ti preghiamo di accettare il trattamento dei dati personali [Si/No].\n"
            " Trovi la nostra privacy policy all'indirizzo https://cacciacapitale.sytes.net/privacypolicy.txt",
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
    key = "id"


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
            "Per inviarcelo clicca sul bottone in basso",
            reply_markup=_markup,
        )
        return self.num

    def process(self, update, context):
        chat_id = update.message.chat_id
        Hunter.objects.create(id=chat_id, phone=update.message.contact.phone_number)
        return self.make_new(update, context)

    filter = Filters.contact
    key = "phone"


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
    key = "name"


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
    key = "surname"


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
    key = "age"


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
    key = "uni"


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
    key = "tframe"


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
    key = "perc"

# Handling the process of assigning a captain
class Grouping:  # others questions are in personalQuestions.py
    def make(self, update, context):
        MAX_MEMBERS_PER_TEAM = Bot_Table.objects.first().max_team_size
        BUTTONS = [[i] for i in cap_anag_list(MAX_MEMBERS_PER_TEAM)]
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
            queue = Queue.objects.create(situation="requested own team", hunter=hunter)
            return self.make_new(update, context)
        cap_anag = choice
        queue = Queue.objects.create(situation="processing", hunter=hunter)
        create_nodes(cap_anag, queue)
        handle_queue(hunter, context)
        return self.make_new(update, context)

    class Filter(BaseFilter):
        def filter(self, message):
            try:
                txt = message.text
                MAX_MEMBERS_PER_TEAM = Bot_Table.objects.first().max_team_size
                flat_buttons = cap_anag_list(MAX_MEMBERS_PER_TEAM)
                flat_buttons.insert(0, "Crea la tua squadra")
                return txt in flat_buttons
            except AttributeError:
                return False

    filter = Filter()
    key = "queue"
