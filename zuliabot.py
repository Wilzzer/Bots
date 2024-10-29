import logging
import string
import time
import json
from datetime import datetime, timedelta
from spellchecker import SpellChecker
from unidecode import unidecode
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
from functools import wraps

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level = logging.INFO
)

RES_FOLDER = "Ressources/"
WHITELIST_FILE = RES_FOLDER+"zul_admin_list.txt"
TOKEN_FILE = RES_FOLDER+"bot_tok.txt"
FORTNITE_FILE = RES_FOLDER+"frontine.mp3"
INOX_FILE = RES_FOLDER+"inxotarag.mp3"
FUTURE_INVESS_FILE = RES_FOLDER+"future_invess.txt"

LSB_ID = "-1001967405759"

WHITELIST_KEY = "whitelist"
LSBLIST_KEY = "lsblist"
FUTURELSB_KEY = "futurelsb"

shitpost_handlers = []

ZUL = ["o",
       "eau",
       "au",
       "aux",
       "oh",
       "ot",
       "ots",
       "ow",
       "aud",
       "aut",
       "os"]

CKU = ["seku",
       "secu",
       "ceku",
       "cecu"]

APAGN = ["apagn",
         "gnan"]

BAN = ["miros",
       "os",
       "bot",
       "hotspot",
       "zuliabot",
       "nullos",
       "aux",
       "au",
       "matos",
       "doritos",
       "faut",
       "bios",
       "ddos",
       "qos",
       "albatros",
       "albinos",
       "craignos",
       "asclepios",
       "tetanos",
       "calvados",
       "galapagos",
       "intramuros",
       "gratos",
       "thermos",
       "pratos",
       "rapidos",
       "tekos",
       "hop",
       "oh",
       "igloo"]

EXCEPT = ["sirop",
          "galop",
          "salop"
          "trop"]

MACRON = ["macron",
          "micron"]

FORTNITE = ["fortnite",
            "frontine",
            "fortnie",
            "fonritne",
            "forntie",
            "frontirne",
            "fornitne",
            "forntine",
            "michou"]

INOX = ["inox",
        "inoxtag",
        "ines"]

def retrieve_auth_users():
    admin_users = []
    with open(WHITELIST_FILE, "r") as whitelist:
        for line in whitelist:
            admin_users.append(line.rstrip())
    return admin_users

def retrieve_future_invess():
    future_invess = []
    with open(FUTURE_INVESS_FILE, "r") as futureinvess:
        for line in futureinvess:
            future_invess.append(line.rstrip())
    return future_invess

async def retrieve_lsb_list(bot):
    lsb_list = await bot.get_chat_administrators(LSB_ID)
    lsb_list_dict = {}
    for lsb_user in lsb_list:
        lsb_list_dict[lsb_user.user.username] = lsb_user.user.id
    return lsb_list_dict

def add_invess(new_invess, bot_data):
    if(new_invess != '' and (new_invess not in bot_data[LSBLIST_KEY]) and (new_invess not in bot_data[FUTURELSB_KEY])):
        bot_data[FUTURELSB_KEY].append(new_invess)
        with open(FUTURE_INVESS_FILE, "a") as f:
            f.write(new_invess+"\n")
        print(new_invess)
        return True
    else:
        return False
    

def add_admin(new_admin, bot_data):
    if(new_admin != '' and (new_admin not in bot_data[WHITELIST_KEY]) and (new_admin not in bot_data[WHITELIST_KEY])):
        bot_data[WHITELIST_KEY].append(new_admin)
        with open(WHITELIST_FILE, "a") as f:
            f.write(new_admin+"\n")
        print(new_admin)
        return True
    else:
        return False

def remove_invess(invess, bot_data):
    if(invess in bot_data[FUTURELSB_KEY]):
        bot_data[FUTURELSB_KEY].remove(invess)
        print(bot_data)
        with open(FUTURE_INVESS_FILE, "r") as f:
            lines = f.readlines()
        with open(FUTURE_INVESS_FILE, "w") as f:
            for line in lines:
                print(line)
                if line.strip("\n") != str(invess):
                    print(line)
                    f.write(line)
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
                    f.write(line+"\n")
        return True
    return False

def restricted(func):
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        if(WHITELIST_KEY not in context.bot_data):
            print("Creating admin list")
            context.bot_data[WHITELIST_KEY] = retrieve_auth_users()
        if(LSBLIST_KEY not in context.bot_data):
            print("Retrieving LSB")
            context.bot_data[LSBLIST_KEY] = await retrieve_lsb_list(context.bot)
            print(context.bot_data[LSBLIST_KEY])
        if(FUTURELSB_KEY not in context.bot_data):
            context.bot_data[FUTURELSB_KEY] = retrieve_future_invess()
        user_id = str(update.effective_user.id)
        print(user_id)
        if(user_id not in context.bot_data[WHITELIST_KEY]):
            text = f"nn ta pa accer ^^ {str(update.effective_user.username)}."
            print(text)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Bonjour, résolvez mes mystères pour devenir investisseur.")

@restricted
async def admincommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.effective_user.first_name+" :", end='')
    print(update.message.text)
    if('listfutureinvess' in update.message.text):
        if(context.bot_data[FUTURELSB_KEY] != []):
            textlist = ""
            for invess in context.bot_data[FUTURELSB_KEY]:
                textlist = textlist+invess+"\n"
            await context.bot.send_message(chat_id=update.effective_chat.id, text=textlist)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Pas de futur investisseur pour le moment.")
    if('addfutureinvess' in update.message.text and context.args):
        answer = add_invess(context.args[0], context.bot_data)
        if(answer):await context.bot.send_message(chat_id=update.effective_chat.id, text="Nouvo future invess :"+context.args[0])
        else:await context.bot.send_message(chat_id=update.effective_chat.id, text=context.args[0]+" déjà dans la list des futurs invess")
    elif("removefutureinvess" in update.message.text and context.args):
        answer = remove_invess(context.args[0], context.bot_data)
        if(answer):await context.bot.send_message(chat_id=update.effective_chat.id, text=context.args[0]+" nest plu un (1) futur invess")
        else:await context.bot.send_message(chat_id=update.effective_chat.id, text=context.args[0]+" est pa un futur invess donc peu pas leenlever")
    if("newadmin" in update.message.text and context.args and str(update.effective_user.id) == str(context.bot_data[WHITELIST_KEY][0])):
        answer = add_admin(context.args[0], context.bot_data)
        if(answer):await context.bot.send_message(chat_id=update.effective_chat.id, text="Nouvo admin :"+context.args[0])
        else:await context.bot.send_message(chat_id=update.effective_chat.id, text=context.args[0]+" deaj admin")
    elif("removeadmin" in update.message.text and context.args and str(update.effective_user.id) == str(context.bot_data[WHITELIST_KEY][0])):
        answer = remove_admin(context.args[0], context.bot_data)
        if(answer):await context.bot.send_message(chat_id=update.effective_chat.id, text=context.args[0]+" plu admin")
        else:await context.bot.send_message(chat_id=update.effective_chat.id, text=context.args[0]+" pa amdin")
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

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    translator = str.maketrans('','',string.punctuation)
    words = update.message.text.lower().translate(translator)
    words = unidecode(words).split()    
    inox = False
    print(update.effective_user.first_name+" :", end='')
    print(words)
    for word in words:
        for o in ZUL:
            if ((word.endswith(o) and word not in BAN) or (word in EXCEPT)):
                zuliatext = "🤌🤌 "+word.upper()+" ZULIANI 🤌🤌"
                await context.bot.send_message(chat_id=update.effective_chat.id, text=zuliatext)
                time.sleep(0.1)
                break
        for apagnan in APAGN:
            if apagnan in word:
                await context.bot.send_animation(chat_id=update.effective_chat.id, animation="CgACAgQAAxkBAANEZgKWAAGeKiZ8tN_8mlRYZXmFAsxOAAJWBAACSYsdUUzZMU2eWmqVNAQ", reply_to_message_id=update.message.id)
                return
        for secu in CKU:
            if secu in word:
                await context.bot.send_sticker(chat_id=update.effective_chat.id, sticker="CAACAgQAAxkBAANWZgKkKTBWXw4QXdnnzj4moP-PuYEAApQJAAIO6MlQCDZWevZwWR40BA", reply_to_message_id=update.message.id)
                break
        
        if word in FORTNITE:
            await context.bot.send_audio(chat_id=update.effective_chat.id, audio=open(FORTNITE_FILE, 'rb'), reply_to_message_id=update.message.id)
        
        if ((word in INOX) and (not inox)):
            await context.bot.send_audio(chat_id=update.effective_chat.id, audio=open(INOX_FILE, 'rb'), reply_to_message_id=update.message.id)
            inox = True

        if(word in MACRON):
            await context.bot.send_animation(chat_id=update.effective_chat.id, animation="CgACAgQAAxkBAAPjZgK8HwXQvB1F_XjHnuGsfGMHlvMAAmwDAALf4wRQ5tyY4x_PPR00BA", reply_to_message_id=update.message.id)

async def apagn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if(update.message.sticker.file_unique_id == "AgADQgAD5ytyDg"):
            # await context.bot.send_sticker(chat_id=update.effective_chat.id, sticker="CAACAgEAAxkBAANPZgKb7zdtIT4QlhlazTLFUHgC6UIAAkIAA-crcg7_CaON3C-qvjQE")
            await context.bot.send_sticker(chat_id=update.effective_chat.id, sticker="CAACAgEAAxkBAAOJZgKo7r4mSNECAaTioqygAAFKuhM0AAJaAAPnK3IO162ahmg5xbs0BA")
            await context.bot.send_sticker(chat_id=update.effective_chat.id, sticker="CAACAgEAAxkBAAOTZgKpDSpkSGH49kaHGyfdHP0RQm0AAlAAA-crcg5tufLQoJOWgjQE")
            await context.bot.send_sticker(chat_id=update.effective_chat.id, sticker="CAACAgEAAxkBAAOeZgKpWvRp3iMXJ72JIz88H-TzJtkAAjwAA-crcg5U6vF3QF9_YjQE")
            await context.bot.send_sticker(chat_id=update.effective_chat.id, sticker="CAACAgEAAxkBAAOfZgKpXSmNYCpguivHpyRgptv0TcwAAjYAA-crcg7a6HRrqVAoYTQE")
            await context.bot.send_sticker(chat_id=update.effective_chat.id, sticker="CAACAgEAAxkBAAOgZgKpXtPhk7QatdTa06L95t-SbPYAAiYAA-crcg52mJjQ8RGlUTQE")
            await context.bot.send_sticker(chat_id=update.effective_chat.id, sticker="CAACAgEAAxkBAAOhZgKpYIeOkh8LjY3iquq1FEVhCsgAAkAAA-crcg5Zul2GzFC4IjQE")
            await context.bot.send_sticker(chat_id=update.effective_chat.id, sticker="CAACAgEAAxkBAAOfZgKpXSmNYCpguivHpyRgptv0TcwAAjYAA-crcg7a6HRrqVAoYTQE")
    except:
        print("Cheh")
    try:
        print(update.message.sticker.file_unique_id)
        print(update.message.sticker.file_id)
    except:
        print(update.message.animation.file_id)

async def invess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if(FUTURELSB_KEY not in context.bot_data):
        context.bot_data[FUTURELSB_KEY] = retrieve_future_invess()
    if(WHITELIST_KEY not in context.bot_data):
        context.bot_data[WHITELIST_KEY] = retrieve_auth_users()
    if(str(update.effective_user.username) in context.bot_data[FUTURELSB_KEY] or str(update.effective_user.id) in context.bot_data[FUTURELSB_KEY] or str(update.effective_user.id) in context.bot_data[WHITELIST_KEY]):
        spell = SpellChecker(language='fr')
        words = update.message.text.lower().split()
        if(words and len(words)>17):
            misspelled = spell.unknown(words)
            if(len(misspelled)>6):
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Barvo ivnvesstreiouers..")
                try:
                    now = datetime.now()
                    expire = now+timedelta(minutes=10)
                    invite_link = await context.bot.create_chat_invite_link(LSB_ID, expire, creates_join_request=True)
                    await context.bot.send_message(chat_id=update.effective_chat.id, text="Bienvnueer au royaume du rire (rire): "+invite_link.invite_link)
                except Exception as e:
                    print("Raté: ")
                    print(e)
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Vrai investisseur écrit correctement")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Vrai blékien écrit autant que le chiffre sacré")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Désolé, tu n'es pas dans la liste des futurs investisseurs")

def main():
    with open(TOKEN_FILE) as f:
        token_file = json.load(f)
    token = token_file['zul']
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler('start', start))
    global shitpost_handlers
    shitpost_handlers.append(MessageHandler(filters.TEXT & (~filters.COMMAND) & filters.ChatType.GROUPS, echo))
    app.add_handler(shitpost_handlers[-1])
    shitpost_handlers.append(MessageHandler((filters.Sticker.ALL | filters.ANIMATION) & filters.ChatType.GROUPS, apagn))
    app.add_handler(shitpost_handlers[-1])
    # app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND) & filters.ChatType.GROUPS, echo))
    # app.add_handler(MessageHandler((filters.Sticker.ALL | filters.ANIMATION) & filters.ChatType.GROUPS, apagn))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND) & filters.ChatType.PRIVATE, invess))
    
    app.add_handler(CommandHandler(command=['addfutureinvess', 'removefutureinvess', 'listfutureinvess','newadmin', 'enableshitpost', 'disableshitpost', 'removeadmin'], callback=admincommand, filters=filters.COMMAND))
    app.add_handler(CommandHandler(['getuserid'], getuserid, filters=filters.COMMAND))
    app.run_polling()

if __name__ == '__main__':
    main()
