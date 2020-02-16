from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .utils import info_summary
from .models import Captain, Hunter, Node

#Initializes the status of a member, given the captain chosen on the chat
def create_nodes(cap_anag, queue):
    cap_list = Captain.objects.all()
    for i in range(len(cap_list)):
      Node.objects.create(
        queue=queue,
        captain=cap_list[i],
        number=i,
        status="Not Asked")
    asked_captain = Captain.objects.get(anagraphic=cap_anag)
    asked_node = Node.objects.get(captain=asked_captain)
    asked_node.status = "Asked"
    asked_node.save()


def handle_queue(hunter, context):
    # choosing the captain which must be asked
      queue = hunter.queue
      node_list = queue.node_set.all()
      status_list = [node.status for node in node_list]
      qlen = len(node_list)
      hunter_id = hunter.id
      for i in range(qlen):
        if status_list[i] == "Not Asked" and status_list[(i - 1) % qlen] == "Refused"\
          or status_list[i] == "Asked":
          node = node_list[i] #node is chosen, if possible
          break
      else: #no captain lasted, all already refused
        context.bot.send_message(chat_id=hunter_id, text="Ci dispiace, la tua iscrizione è stata negata "
          "(le squadre potrebbero essere al completo). Puoi comunque partecipare alla caccia creando una nuova squadra.")
        queue.situation = "refused by all"
        queue.save()
        return
      # making the question to chosen captain
      cap_id = node.captain.id
      buttons_list = [
        [InlineKeyboardButton("Si", callback_data="*".join(["Si", str(hunter_id)]))],
        [InlineKeyboardButton("No", callback_data="*".join(["No", str(hunter_id)]))]
      ]
      reply_markup = InlineKeyboardMarkup(buttons_list)
      node.status = "Asked"
      node.save()
      context.bot.send_message(
        chat_id=cap_id,
        text=info_summary(hunter=hunter),
        reply_markup=reply_markup
      )


def cap_queue_callback(update, context):
    query = update.callback_query
    answer, hunter_id_str= query.data.split("*")
    hunter_id = int(hunter_id_str)
    cap_id = query.message.chat_id

    context.bot.edit_message_reply_markup(
         chat_id=cap_id,
         message_id=query.message.message_id,
         reply_markup=None
    )

    cap = Captain.objects.get(id=cap_id)
    hunter = Hunter.objects.get(id=hunter_id)
    node = hunter.queue.node_set.get(captain=cap)

    if answer == "Si":
        node.status = "Accepted"
        hunter.captain = cap
        context.bot.send_message(chat_id=cap_id, text="Perfetto, iscrizione accettata")
        context.bot.send_message(chat_id=hunter_id, text="La tua iscrizione è stata confermata.\n"
          "Sei stato inserito nella squadra di: " + cap.anagraphic)
        hunter.queue.situation = "accepted by someone"
        node.save()
        hunter.save()
    if answer == "No":
        node.status = "Refused"
        context.bot.send_message(chat_id=cap_id, text="Perfetto, iscrizione rifiutata")
        node.save()
        handle_queue(hunter, context)
