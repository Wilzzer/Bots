import logging
import string
import time
import json
from unidecode import unidecode
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level = logging.INFO
)

TOKEN_FILE = "Ressources/bot_tok.txt"
FORTNITE_FILE = "Ressources/frontine.mp3"

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
            "inoxtag",
            "michou"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    translator = str.maketrans('','',string.punctuation)
    words = update.message.text.lower().translate(translator)
    words = unidecode(words).split()    
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
        # if word in APAGN:
                await context.bot.send_animation(chat_id=update.effective_chat.id, animation="CgACAgQAAxkBAANEZgKWAAGeKiZ8tN_8mlRYZXmFAsxOAAJWBAACSYsdUUzZMU2eWmqVNAQ", reply_to_message_id=update.message.id)
                return
        for secu in CKU:
            if secu in word:
        # if(word in CKU):
                await context.bot.send_sticker(chat_id=update.effective_chat.id, sticker="CAACAgQAAxkBAANWZgKkKTBWXw4QXdnnzj4moP-PuYEAApQJAAIO6MlQCDZWevZwWR40BA", reply_to_message_id=update.message.id)
                break
        
        if word in FORTNITE:
            await context.bot.send_audio(chat_id=update.effective_chat.id, audio=open(FORTNITE_FILE, 'rb'), reply_to_message_id=update.message.id)
        
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

    
def main():
    with open(TOKEN_FILE) as f:
        token_file = json.load(f)
    token = token_file['zul']
    app = ApplicationBuilder().token(token).build()

    # app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))
    app.add_handler(MessageHandler(filters.Sticker.ALL | filters.ANIMATION, apagn))

    app.run_polling()


if __name__ == '__main__':
    main()
