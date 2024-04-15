import os
import json
import telegram
import re
from datetime import datetime
from telegram import Update
from functools import wraps
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

RES_FOLDER = "Ressources/"
TOKEN_FILE = RES_FOLDER+"bot_tok.txt"
WHITELIST_FILE = RES_FOLDER+"admin_list.txt"

DRIVE_KEY = "drive"
WHITELIST_KEY = "whitelist"
ACTIF_KEY = "actif"

DRIVE_SETTINGS = {
        "client_config_backend": "file",
        "client_config_file": RES_FOLDER+"client_secrets.json",
        "save_credentials": False,
        "oauth_scope": ["https://www.googleapis.com/auth/drive"],
    }


def upload_to_google_drive(drive, file_path):
    metadata = {
        'parents':[{"id":"1iwCmOMPB8eFM1rtQMHW_QNiXOu0cK-BP"}],
        'title':os.path.basename(file_path)
    }
    file_drive = drive.CreateFile(metadata=metadata)
    file_drive.SetContentFile(file_path)
    file_drive.Upload()

def authenticate_drive():
    gauth = GoogleAuth(settings=DRIVE_SETTINGS)
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    return drive

def retrieve_auth_users():
    admin_users = []
    with open(WHITELIST_FILE, "r") as whitelist:
        for line in whitelist:
            admin_users.append(line.rstrip())
    return admin_users

def restricted(func):
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        if(WHITELIST_KEY not in context.bot_data):
            print("Creating admin list")
            context.bot_data[WHITELIST_KEY] = retrieve_auth_users()
        user_id = str(update.effective_user.id)
        print(user_id)
        if(user_id not in context.bot_data[WHITELIST_KEY]):
            text = f"COMMANDS DENIED FOR {user_id}."
            print(text)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

async def save_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} ({}) sent a photo".format(update.message.from_user.first_name, update.message.from_user.id))
    if (context.bot_data[ACTIF_KEY]):
        if(update.message.photo):
            file_id = update.message.photo[-1].file_id
            file = await context.bot.get_file(file_id)
        else:
            file = await update.message.effective_attachment.get_file()

        now = datetime.now()
        filename = f"{RES_FOLDER}/{update.message.from_user.first_name}_{now.strftime('%d_%m_%Y__%H:%M:%S')}"
        await file.download_to_drive(filename)

        upload_to_google_drive(context.bot_data[DRIVE_KEY], filename)
        await context.bot.send_sticker(chat_id=update.effective_chat.id, sticker="CAACAgQAAxkBAAIDAAFmHS3yhan2ZHcGr3AOzUxfdTYpPwACJgADo2BSJe5Iq58LIBQrNAQ")

@restricted
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if("newadmin" in update.message.text):
        res = re.search("/newadmin", update.message.text)
        newadmin_id = update.message.text[res.end()+1:].rstrip()
        if(newadmin_id != '' and newadmin_id not in context.bot_data[WHITELIST_KEY]):
            context.bot_data[WHITELIST_KEY].append(newadmin_id)
            print(context.bot_data)
            with open(WHITELIST_FILE, "a") as f:
                f.write(newadmin_id)
    elif("removeadmin" in update.message.text and str(update.effective_user.id) == str(context.bot_data[WHITELIST_KEY][0])):
        res = re.search("/removeadmin", update.message.text)
        remadmin_id = update.message.text[res.end()+1:].rstrip()
        if(remadmin_id in context.bot_data[WHITELIST_KEY]):
            context.bot_data[WHITELIST_KEY].remove(remadmin_id)
            print(context.bot_data)
            with open(WHITELIST_FILE, "r") as f:
                lines = f.readlines()
            with open(WHITELIST_FILE, "w") as f:
                for line in lines:
                    if line.strip("\n") != str(remadmin_id):
                        f.write(line)
    elif("actif" in update.message.text and not context.bot_data[ACTIF_KEY]):
        print("Bot actif")
        context.bot_data[ACTIF_KEY] = True
    elif("inactif" in update.message.text and context.bot_data[ACTIF_KEY]):
        print("Bot inactif")
        context.bot_data[ACTIF_KEY] = False

def main():
    drive = authenticate_drive()

    with open(TOKEN_FILE) as f:
        token_file = json.load(f)
    token = token_file['drive']
    app = ApplicationBuilder().token(token).build()
    app.bot_data[DRIVE_KEY] = drive
    app.bot_data[ACTIF_KEY] = True

    app.add_handler(CommandHandler(['newadmin', 'actif', 'inactif', 'removeadmin'], admin_command, filters=filters.COMMAND))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.IMAGE, save_image))
    app.run_polling()

if __name__ == '__main__':
    main()
