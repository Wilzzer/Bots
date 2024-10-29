import logging
import string
import time
import json
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, ConversationHandler, CallbackQueryHandler
from functools import wraps

# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level = logging.INFO
# )

RES_FOLDER = "Ressources/"
WHITELIST_FILE = RES_FOLDER+"clark_admin_list.txt"
CLARKLIST_FILE = RES_FOLDER+"clark_list.txt"
CARISTELIST_FILE = RES_FOLDER+"cariste_list.txt"
TOKEN_FILE = RES_FOLDER+"bot_tok.txt"

CLARK_GROUP_ID = "-1001967405759"

MSG_KEY = "message_actuel"
HASCLARK_KEY = "hasclark"

WHITELIST_KEY = "whitelist"
CLARKLIST_KEY = "clarklist"
CARISTELIST_KEY = "caristelist"
FUTURELSB_KEY = "futurelsb"

shitpost_handlers = []

MAIN_MENU, PARK_PREC, MISSION_UPDATE = range(3)

class Clark:
    def __init__(self, name, driver="Aucun", state="Garé", mission="Aucune"):
        self.driver = driver
        self.name = name
        self.state = state
        self.mission = mission
        self.tcharge = None

def retrieve_auth_users():
    admin_users = []
    with open(WHITELIST_FILE, "r") as whitelist:
        for line in whitelist:
            admin_users.append(line.rstrip())
    return admin_users

def retrieve_clark_list():
    clarks = []
    with open(CLARKLIST_FILE, "r") as clarklist:
        for line in clarklist:
            clarks.append(Clark(line.rstrip()))
    return clarks

def retrieve_cariste_list():
    caristes = []
    with open(CARISTELIST_FILE, "r") as caristelist:
        for line in caristelist:
            caristes.append(line.rstrip())
    return caristes

def add_admin(new_admin, bot_data):
    if(new_admin != '' and (new_admin not in bot_data[WHITELIST_KEY])):
        bot_data[WHITELIST_KEY].append(new_admin)
        with open(WHITELIST_FILE, "a") as f:
            f.write(new_admin+"\n")
        print(new_admin)
        return True
    else:
        return False

def remove_admin(admin, bot_data):
    if(admin in bot_data[WHITELIST_KEY]):
        bot_data[WHITELIST_KEY].remove(admin)
        print(bot_data)
        with open(WHITELIST_FILE, "r") as f:
            lines = f.readlines()
        with open(WHITELIST_FILE, "w") as f:
            for line in lines:
                if line.strip("\n") != str(admin):
                    f.write(line)
        return True
    return False

def add_clark(new_clark, bot_data):
    if(new_clark != '' and not any(clark.name == new_clark for clark in bot_data[CLARKLIST_KEY])):
        bot_data[CLARKLIST_KEY].append(Clark(new_clark))
        with open(CLARKLIST_FILE, "a") as f:
            f.write(new_clark+"\n")
        print(new_clark)
        return True
    else:
        return False
    
def remove_clark(clark, bot_data):
    if any(clarks.name == clark for clarks in bot_data[CLARKLIST_KEY]):
        for clarks in bot_data[CLARKLIST_KEY]:
            if (clarks.name == clark):
                bot_data[CLARKLIST_KEY].remove(clarks)
                break
        print(bot_data)
        with open(CLARKLIST_FILE, "r") as f:
            lines = f.readlines()
        with open(CLARKLIST_FILE, "w") as f:
            for line in lines:
                if line.strip("\n") != str(clark):
                    f.write(line)
        return True
    return False

def add_cariste(new_cariste, bot_data):
    if(new_cariste != '' and (new_cariste not in bot_data[CARISTELIST_KEY])):
        bot_data[CARISTELIST_KEY].append(new_cariste)
        with open(CARISTELIST_FILE, "a") as f:
            f.write(new_cariste+"\n")
        print(new_cariste)
        return True
    else:
        return False
    
def remove_cariste(cariste, bot_data):
    if(cariste in bot_data[CARISTELIST_KEY]):
        bot_data[CARISTELIST_KEY].remove(cariste)
        print(bot_data)
        with open(CARISTELIST_FILE, "r") as f:
            lines = f.readlines()
        with open(CARISTELIST_FILE, "w") as f:
            for line in lines:
                if line.strip("\n") != str(cariste):
                    f.write(line)
        return True
    return False

def restricted(func):
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        if(WHITELIST_KEY not in context.bot_data):
            print("Creating admin list")
            context.bot_data[WHITELIST_KEY] = retrieve_auth_users()
        if(CLARKLIST_KEY not in context.bot_data):
            print("Retrieving clark list")
            context.bot_data[CLARKLIST_KEY] = retrieve_clark_list()
            print(context.bot_data[CLARKLIST_KEY])
        if(CARISTELIST_KEY not in context.bot_data):
            context.bot_data[CARISTELIST_KEY] = retrieve_cariste_list()
        user_id = str(update.effective_user.id)
        print(user_id)
        if(user_id not in context.bot_data[WHITELIST_KEY]):
            text = f"Vous n'avez pas accès à cette commande, {str(update.effective_user.username)}."
            print(text)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

def cariste_restricted(func):
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        if(CLARKLIST_KEY not in context.bot_data):
            print("Retrieving clark list")
            context.bot_data[CLARKLIST_KEY] = retrieve_clark_list()
            print(context.bot_data[CLARKLIST_KEY])
        if(CARISTELIST_KEY not in context.bot_data):
            context.bot_data[CARISTELIST_KEY] = retrieve_cariste_list()
        user_id = str(update.effective_user.id)
        print(update.effective_user.full_name+" ("+user_id+") essaie d'accéder aux commandes cariste.")
        if(user_id not in context.bot_data[CARISTELIST_KEY]):
            text = f"Vous n'avez pas accès à cette commande, {str(update.effective_user.username)}."
            print(text)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # await context.bot.send_message(chat_id=update.effective_chat.id, text="Bonjour et bienvenue dans le gestionnaire de clarks de Balélec. Entrez '/balkany' pour gérer les clarks.")
    await update.message.reply_text("Envie de clarkistaner ?", reply_markup=ReplyKeyboardMarkup([["CLARKISTANING"]], one_time_keyboard=False, input_field_placeholder="Clarkistan?"))

@restricted
async def admincommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.effective_user.first_name+" :", end='')
    print(update.message.text)
    if('addclark' in update.message.text and context.args):
        answer = add_clark(context.args[0], context.bot_data)
        if(answer):await context.bot.send_message(chat_id=update.effective_chat.id, text="Nouveau clark ajouté : "+context.args[0])
        else:await context.bot.send_message(chat_id=update.effective_chat.id, text=context.args[0]+" est déjà dans la liste des clarks.")
    elif("removeclark" in update.message.text and context.args):
        if(len(context.bot_data[CLARKLIST_KEY])!=0):
            answer = remove_clark(context.args[0], context.bot_data)
            if(answer):await context.bot.send_message(chat_id=update.effective_chat.id, text=context.args[0]+" n'est plus dans la liste des clarks.")
            else:
                text =context.args[0]+" ne fait pas parti des clarks actifs. Les clarks actifs sont les suivants: "
                clarklist_txt = ""
                for clark in context.bot_data[CLARKLIST_KEY]:
                    if(clarklist_txt==""): clarklist_txt=clarklist_txt+"'"+clark.name+"'"
                    else:clarklist_txt=clarklist_txt+", '"+clark.name+"'"
                text = text+clarklist_txt
                await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        else: await context.bot.send_message(chat_id=update.effective_chat.id, text="Il n'y a pas de clark enregistré pour le moment.")
    if('addcariste' in update.message.text and context.args):
        answer = add_cariste(context.args[0], context.bot_data)
        if(answer):await context.bot.send_message(chat_id=update.effective_chat.id, text="Nouveau cariste ajouté : "+context.args[0])
        else:await context.bot.send_message(chat_id=update.effective_chat.id, text=context.args[0]+" est déjà dans la liste des caristes.")
    elif("removecariste" in update.message.text and context.args):
        if(len(context.bot_data[CARISTELIST_KEY])!=0):
            answer = remove_cariste(context.args[0], context.bot_data)
            if(answer):await context.bot.send_message(chat_id=update.effective_chat.id, text=context.args[0]+" n'est plus dans la liste des caristes.")
            else:
                text =context.args[0]+" ne fait pas parti des caristes actifs. Les caristes actifs sont les suivants: "
                caristes_txt = ""
                for cariste in context.bot_data[CARISTELIST_KEY]:
                    if(caristes_txt==""): caristes_txt=caristes_txt+"'"+cariste+"'"
                    else:caristes_txt=caristes_txt+", '"+cariste+"'"
                text = text+caristes_txt
                await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        else: await context.bot.send_message(chat_id=update.effective_chat.id, text="Il n'y a pas de cariste enregistré pour le moment.")
    if("newadmin" in update.message.text and context.args and str(update.effective_user.id) == str(context.bot_data[WHITELIST_KEY][0])):
        answer = add_admin(context.args[0], context.bot_data)
        if(answer):await context.bot.send_message(chat_id=update.effective_chat.id, text="Nouvel admin :"+context.args[0])
        else:await context.bot.send_message(chat_id=update.effective_chat.id, text=context.args[0]+" est déjà admin")
    elif("removeadmin" in update.message.text and context.args and str(update.effective_user.id) == str(context.bot_data[WHITELIST_KEY][0])):
        answer = remove_admin(context.args[0], context.bot_data)
        if(answer):await context.bot.send_message(chat_id=update.effective_chat.id, text=context.args[0]+" n'est plus admin")
        else:await context.bot.send_message(chat_id=update.effective_chat.id, text=context.args[0]+" n'est pas un admin")
    elif("enableshitpost" in update.message.text):
        global shitpost_handlers
        if(shitpost_handlers == []):
            shitpost_handlers.append(MessageHandler(filters.TEXT & (~filters.COMMAND) & filters.ChatType.GROUPS, echo))
            context.application.add_handler(shitpost_handlers[-1])
            shitpost_handlers.append(MessageHandler((filters.Sticker.ALL | filters.ANIMATION) & filters.ChatType.GROUPS, apagn))
            context.application.add_handler(shitpost_handlers[-1])
            await context.bot.send_message(chat_id=update.effective_chat.id, text="près a shitpostère")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="deaj entr1 de shitooiprs")
    elif("disableshitpost" in update.message.text):
        if(shitpost_handlers != []):
            for handler in shitpost_handlers:
                context.application.remove_handler(handler)
            shitpost_handlers = []
            await context.bot.send_message(chat_id=update.effective_chat.id, text="shitpots annuler")

async def getuserid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.effective_user.id)

@cariste_restricted
async def start_gestion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    text = "Que souhaitez-vous faire ?"
    buttons = [[InlineKeyboardButton("Gérer un clark", callback_data="gestion_clark"), InlineKeyboardButton("Consulter les clarks", callback_data="consulter_clark")],
               [InlineKeyboardButton("Annuler", callback_data="cancel")]]
    if(query):await update_msg(update, context, text, buttons)
    else:context.user_data[MSG_KEY] = await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=InlineKeyboardMarkup(buttons))
    if(HASCLARK_KEY not in context.user_data): context.user_data[HASCLARK_KEY] = False
    return MAIN_MENU

async def gestion_clark(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = "Que souhaitez-vous faire ?"
    if(context.user_data[HASCLARK_KEY]):
        buttons = [[InlineKeyboardButton("🔙", callback_data="start_gestion")],
                   [InlineKeyboardButton("Rendre son clark", callback_data="release_clark"), InlineKeyboardButton("Gestion de mission", callback_data="gestion_mission")],
                   [InlineKeyboardButton("Annuler", callback_data="cancel")]]
    else:
        buttons = [[InlineKeyboardButton("🔙", callback_data="start_gestion")],
                   [InlineKeyboardButton("Prendre un clark", callback_data="use_clark")],
                   [InlineKeyboardButton("Annuler", callback_data="cancel")]]
    
    await update_msg(update, context, text, buttons)
    return MAIN_MENU

async def gestion_mission(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = "Écrivez ici votre mission"
    await update_msg(update, context, text, [])
    return MISSION_UPDATE

async def gestion_mission_detail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    for clark in context.bot_data[CLARKLIST_KEY]:
        if(clark.driver == update.effective_user.full_name):
            clark.mission = update.message.text
            break
    text = "Mission mise à jour."
    print(update.effective_user.full_name + " a mis à jour sa mission :'"+update.message.text+"'")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    return ConversationHandler.END

async def use_clark(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if(not context.user_data[HASCLARK_KEY]):
        text = "Quel clark souhaitez-vous utiliser ?"
        buttons = [[InlineKeyboardButton("🔙", callback_data="gestion_clark")]]
        clark_buttons = []
        for clark in context.bot_data[CLARKLIST_KEY]:
            if(clark.driver == "Aucun"):
                clark_buttons.append(InlineKeyboardButton(clark.name, callback_data="select_"+clark.name))
            if(len(clark_buttons)==2):
                buttons.append(clark_buttons)
                clark_buttons = []
        if(len(clark_buttons)):buttons.append(clark_buttons)
        buttons.append([InlineKeyboardButton("Annuler", callback_data="cancel")])
    else:
        text = "Vous utilisez déjà un clark."
        buttons = [[InlineKeyboardButton("🔙", callback_data="gestion_clark")],
                   [InlineKeyboardButton("Annuler", callback_data="cancel")]]
    await update_msg(update, context, text, buttons)
    return MAIN_MENU

async def select_clark(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    cname = query.data[query.data.find("_")+1:]
    context.user_data[HASCLARK_KEY] = True
    for clark in context.bot_data[CLARKLIST_KEY]:
        if(clark.name == cname):
            clark.driver = update.effective_user.full_name
            clark.state = "En service"
            break
    text = "Vous utilisez maintenant le "+clark.name+"."
    print(update.effective_user.full_name + " utilise le clark "+cname)
    buttons = [[InlineKeyboardButton("Rendre son clark", callback_data="release_"+cname), InlineKeyboardButton("Gestion de mission", callback_data="gestion_mission")],
               [InlineKeyboardButton("Terminé", callback_data="cancel")]]
    await update_msg(update, context, text, buttons)
    return MAIN_MENU

async def release_clark(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    if(query.data != "release_clark"):cname = query.data[query.data.find("_")+1:]
    else:
        for clark in context.bot_data[CLARKLIST_KEY]:
            if(clark.driver == update.effective_user.full_name):
                cname = clark.name
                break
    context.user_data[HASCLARK_KEY] = False
    text = "Précision rendu"
    buttons = [[InlineKeyboardButton("Parké", callback_data="park_"+cname)], 
               [InlineKeyboardButton("À charger", callback_data="charge_"+cname)]]
    await update_msg(update, context, text, buttons)
    return MAIN_MENU
    
async def park_clark(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = "Où est garé le clark ?"
    await update_msg(update, context, text, [])
    return PARK_PREC

async def park_clark_detail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    for clark in context.bot_data[CLARKLIST_KEY]:
        if(clark.driver == update.effective_user.full_name):
            clark.driver = "Aucun"
            clark.state = "Garé - "+update.message.text
            clark.mission = "Aucune"
            break
    text = "Vous avez rendu le "+clark.name
    print(update.effective_user.full_name + " a garé le clark "+clark.name)
    await update_msg(update, context, text, [])
    return ConversationHandler.END

async def charge_clark(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    cname = query.data[query.data.find("_")+1:]
    print(update.effective_user.full_name + " met à charger le clark "+cname)
    for clark in context.bot_data[CLARKLIST_KEY]:
        if(clark.name == cname):
            clark.driver = "Aucun"
            clark.state = "En charge"
            clark.mission = "Aucune"
            clark.tcharge = datetime.now()
            break
    text = "Vous avez rendu le "+clark.name
    await update_msg(update, context, text, [])
    return ConversationHandler.END

async def consulter_clark(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print(update.effective_user.full_name + " consulte l'état des clarks")
    text = "ÉTAT DES CLARKS\n\n"
    for clark in context.bot_data[CLARKLIST_KEY]:
        clark_data ="--- "+clark.name+" ---\n"+"      -> ÉTAT: "+clark.state
        if(clark.state == "En charge"):
           clark_data=clark_data+" ("
           tcharge = datetime.now()-clark.tcharge
           hours, remainder = divmod(tcharge.seconds, 3600)
           minutes, seconds = divmod(remainder, 60)
           if(hours):clark_data=clark_data+str(hours)+"h, "
           if(minutes):clark_data=clark_data+str(minutes)+"mins et"
           if(seconds):clark_data=clark_data+str(seconds)+"secs"
           clark_data=clark_data+")"

        clark_data=clark_data+"\n      -> Conducteur: "+clark.driver+"\n      -> Mission: "+clark.mission+"\n\n------------\n\n"
        text = text+clark_data
    buttons = [[InlineKeyboardButton("🔙", callback_data="start_gestion")],
               [InlineKeyboardButton("Terminé", callback_data="cancel")]]
    await update_msg(update, context, text, buttons)
    return MAIN_MENU
    
async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = "Terminé"
    await update_msg(update, context, text, [])
    return ConversationHandler.END

async def update_msg(update, context, text, buttons) -> int:
    if(MSG_KEY in context.user_data):await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=context.user_data[MSG_KEY].message_id, text=text, reply_markup=InlineKeyboardMarkup(buttons))
    else: context.user_data[MSG_KEY] = await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=InlineKeyboardMarkup(buttons))

def main():
    with open(TOKEN_FILE) as f:
        token_file = json.load(f)
    token = token_file['clark']
    app = ApplicationBuilder().token(token).build()

    gestion_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler(['balkany'], start_gestion)
        ],
        states={
            MAIN_MENU:[
                CallbackQueryHandler(gestion_clark, pattern="gestion_clark"),
                CallbackQueryHandler(start_gestion, pattern="start_gestion"),
                CallbackQueryHandler(consulter_clark, pattern="consulter_clark"),
                CallbackQueryHandler(gestion_mission, pattern="gestion_mission"),
                CallbackQueryHandler(use_clark, pattern="use_clark"),
                CallbackQueryHandler(select_clark, pattern="select_"),
                CallbackQueryHandler(release_clark, pattern="release_"),
                CallbackQueryHandler(park_clark, pattern="park_"),
                CallbackQueryHandler(charge_clark, pattern="charge_"),
                CallbackQueryHandler(done, pattern="cancel")
            ],
            PARK_PREC:[
                MessageHandler(filters.TEXT, park_clark_detail)
            ],
            MISSION_UPDATE:[
                MessageHandler(filters.TEXT, gestion_mission_detail)
            ]
        },
        fallbacks=[
            MessageHandler(filters.Regex("^(Done|Discard)$"), done)
            ],
        block=False
    )
    app.add_handler(gestion_conv_handler)
    app.add_handler(CommandHandler('start', start))
    
    app.add_handler(CommandHandler(command=['addclark', 'removeclark', 'newadmin', 'removeadmin', 'addcariste', 'removecariste'], callback=admincommand, filters=filters.COMMAND & filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler(['getuserid'], getuserid, filters=filters.COMMAND))
    app.run_polling()

if __name__ == '__main__':
    main()
