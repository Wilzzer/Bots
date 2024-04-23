import os
import json
import re
import string
import time
from datetime import datetime
from telegram import *
from telegram.ext import *
from functools import wraps
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

RES_FOLDER = "Ressources/"
TOKEN_FILE = RES_FOLDER+"bot_tok.txt"
WHITELIST_FILE = RES_FOLDER+"admin_list.txt"

DRIVE_KEY = "drive"
WHITELIST_KEY = "whitelist"
ACTIF_KEY = "actif"

MSG_KEY = "message_actuel"
FILES_KEY = "files"
CURRENT_FOLDER_ID_KEY = "current_folder_id"
CURRENT_FOLDER_KEY = "current_folder"
PARENT_FOLDER_ID_KEY = "parent_folder_id"
PARENT_FOLDER_KEY = "parent_folder"

DRIVE_ROOT_FOLDER = "1iwCmOMPB8eFM1rtQMHW_QNiXOu0cK-BP"
# DRIVE_ROOT_FOLDER = "1L4RwhNTIPACYkO9bM4aGVTr1ZlpHcL7u"
# DRIVE_SETTINGS = {
#         "client_config_backend": "file",
#         "client_config_file": RES_FOLDER+"client_secrets.json",
#         "save_credentials": False,
#         "oauth_scope": ["https://www.googleapis.com/auth/drive"],
#     }
DRIVE_SETTINGS = {
        "client_config_backend": "service",
        "service_config": {
                "client_json_file_path": RES_FOLDER+"service-secrets.json"
            },
        "oauth_scope": ["https://www.googleapis.com/auth/drive"],
    }
FOLDER_MAX_BUTTONS = 2

SAVE_SELECT, FOLDER = range(2)

class GoogleDrivito:
    def __init__(self, folder_id):
        self.gauth = GoogleAuth(settings=DRIVE_SETTINGS)
        self.gauth.ServiceAuth()
        self.drive = GoogleDrive(self.gauth)
        about = self.drive.GetAbout()
        print('Root folder ID:{}'.format(about['rootFolderId']))
        self.root_folder = folder_id

    def upload_file(self, filename, user_data):
        metadata = {
            'parents':[{"id":user_data[CURRENT_FOLDER_ID_KEY]}],
            'title':os.path.basename(filename)
        }
        file_drive = self.drive.CreateFile(metadata=metadata)
        file_drive.SetContentFile(filename)
        file_drive.Upload()

    def create_folder(self, folder_name, user_data):
        metadata = {
            'title':folder_name,
            'parents':[{"id":user_data[CURRENT_FOLDER_ID_KEY]}],
            'mimeType':'application/vnd.google-apps.folder'
        }
        folder = self.drive.CreateFile(metadata=metadata)
        folder.Upload()
        return user_data[CURRENT_FOLDER_ID_KEY], user_data[CURRENT_FOLDER_KEY], folder['id'], folder['title']

    def get_folder_buttons(self, user_data):
        buttons = [[InlineKeyboardButton("Save image here", callback_data="save_here")]]
        row_buttons = []
        time.sleep(0.2)
        q_req = f"'{user_data[CURRENT_FOLDER_ID_KEY]}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        f = self.drive.ListFile({"q": q_req}).GetList()
        for folder in f:
            new_button = InlineKeyboardButton(folder['title'], callback_data=folder['title'])
            row_buttons.append(new_button)
            if(len(row_buttons)==FOLDER_MAX_BUTTONS):
                buttons.append(row_buttons)
                row_buttons = []
        if(len(row_buttons)==1):buttons.append(row_buttons)
        if(self.root_folder == user_data[CURRENT_FOLDER_ID_KEY]):row_buttons = [InlineKeyboardButton("New folder", callback_data="new_folder")]
        else: row_buttons = [InlineKeyboardButton("🔙", callback_data="back_folder"), InlineKeyboardButton("New folder", callback_data="new_folder")]
        buttons.append(row_buttons)

        buttons.append([InlineKeyboardButton("Cancel ❌", callback_data="cancel")])

        return buttons

def retrieve_auth_users():
    admin_users = []
    with open(WHITELIST_FILE, "r") as whitelist:
        for line in whitelist:
            admin_users.append(line.rstrip())
    return admin_users

def remove_emoji(string):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002500-\U00002BEF"  # chinese char
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # dingbats
                               u"\u3030"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)

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

async def retrieve_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data[CURRENT_FOLDER_ID_KEY] = context.bot_data[DRIVE_KEY].root_folder
    context.user_data[CURRENT_FOLDER_KEY] = "root"
    context.user_data[PARENT_FOLDER_ID_KEY] = None
    context.user_data[PARENT_FOLDER_KEY] = ""
    if(FILES_KEY not in context.user_data):context.user_data[FILES_KEY] = []

    print("User {} ({}) sent a photo".format(update.message.from_user.first_name, update.message.from_user.id))
    if (context.bot_data[ACTIF_KEY]):
        try:
            if(update.message.photo):
                file_id = update.message.photo[-1].file_id
                file = await context.bot.get_file(file_id)
            else:
                file = await update.message.effective_attachment.get_file()

            now = datetime.now()
            filename = f"./{RES_FOLDER}{update.message.from_user.first_name}__{now.strftime('%d_%m_%Y__%H-%M-%S-%f')}"
            try:
                await file.download_to_drive(filename)
                context.user_data[FILES_KEY].append(filename)
                buttons = [["Send to drive"]]
                if(MSG_KEY in context.user_data): await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=context.user_data[MSG_KEY].message_id)
                context.user_data[MSG_KEY] = await context.bot.send_message(chat_id=update.effective_chat.id, text="Tell me when you're done sending pictures.", reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True))
                return

            except Exception as e:
                print("Error in downloading or uploading the file. See error: ", e)
                if(MSG_KEY in context.user_data): await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=context.user_data[MSG_KEY].message_id)
                context.user_data[MSG_KEY] = await context.bot.send_message(chat_id=update.effective_chat.id, text="Couldn't load file. Please try again or contact xxx.")
                return
        except Exception as e:
            print("User "+str(update.effective_user.first_name)+ " ("+str(update.effective_user.id)+") tried uploading an image that was too large.")
            if(MSG_KEY in context.user_data): await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=context.user_data[MSG_KEY].message_id)
            context.user_data[MSG_KEY] = await context.bot.send_message(chat_id=update.effective_chat.id, text="Couldn't load file. Your file is probably bigger than 20MB.")

# async def drive_conv_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

async def save_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = f"Saving {len(context.user_data[FILES_KEY])} picture(s) in folder {context.user_data[CURRENT_FOLDER_KEY]}"
    await query.edit_message_text(text=text, reply_markup=None)
    for file in context.user_data[FILES_KEY]:
        context.bot_data[DRIVE_KEY].upload_file(file, context.user_data)
        os.remove(file)
        print("User {} ({}) saved a photo in {}".format(update.effective_user.first_name, update.effective_user.id, context.user_data[CURRENT_FOLDER_KEY]))
    context.user_data[CURRENT_FOLDER_ID_KEY] = context.bot_data[DRIVE_KEY].root_folder
    context.user_data[CURRENT_FOLDER_KEY] = "root"
    context.user_data[PARENT_FOLDER_ID_KEY] = None
    context.user_data[PARENT_FOLDER_KEY] = ""
    del context.user_data[MSG_KEY]
    del context.user_data[FILES_KEY]
    await query.edit_message_text(text="Picture(s) saved.", reply_markup=None)
    await context.bot.send_sticker(chat_id=update.effective_chat.id, sticker="CAACAgQAAxkBAAIDAAFmHS3yhan2ZHcGr3AOzUxfdTYpPwACJgADo2BSJe5Iq58LIBQrNAQ")
    
    return ConversationHandler.END

async def new_folder_req(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Please enter a new folder name", reply_markup=None)

    return FOLDER

async def change_folder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    drive = context.bot_data[DRIVE_KEY]
    if(update.message and (MSG_KEY in context.user_data) and (update.message.text == "Send to drive")):del context.user_data[MSG_KEY]

    try:
        query = update.callback_query
        await query.answer()
        if(query.data != "back_folder"):
            folder_req = query.data
            q_req = f"'{context.user_data[CURRENT_FOLDER_ID_KEY]}' in parents and title = '{folder_req}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            f = drive.drive.ListFile({"q": q_req}).GetList()
            folder = f[0]

            context.user_data[PARENT_FOLDER_ID_KEY] = context.user_data[CURRENT_FOLDER_ID_KEY]
            context.user_data[PARENT_FOLDER_KEY] = context.user_data[CURRENT_FOLDER_KEY]
            context.user_data[CURRENT_FOLDER_ID_KEY] = folder['id']
            context.user_data[CURRENT_FOLDER_KEY] = folder_req
        else: 
            folder_req = context.user_data[CURRENT_FOLDER_KEY]
    except:
        try: folder_req = context.user_data[CURRENT_FOLDER_KEY]
        except Exception as e: print("Error :", e)
    buttons = drive.get_folder_buttons(context.user_data)
    text = "What do you wish to do ?\nCurrently in folder "+folder_req
    if(MSG_KEY in context.user_data):await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=context.user_data[MSG_KEY].message_id, text=text, reply_markup=InlineKeyboardMarkup(buttons))
    else: context.user_data[MSG_KEY] = await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=InlineKeyboardMarkup(buttons))

    return SAVE_SELECT

async def back_folder_req(update: Update, context: ContextTypes.DEFAULT_TYPE):
    drive = context.bot_data[DRIVE_KEY]
    parent_file = drive.drive.CreateFile({'id':context.user_data[PARENT_FOLDER_ID_KEY]})
    parent_file.FetchMetadata()
    context.user_data[CURRENT_FOLDER_ID_KEY] = context.user_data[PARENT_FOLDER_ID_KEY]
    context.user_data[CURRENT_FOLDER_KEY] = context.user_data[PARENT_FOLDER_KEY]
    try:
        new_parent = drive.drive.CreateFile({'id':parent_file['parents'][0]['id']})
        new_parent.FetchMetadata()
        context.user_data[PARENT_FOLDER_ID_KEY] = new_parent['id']
        context.user_data[PARENT_FOLDER_KEY] = new_parent['title']
    except Exception as e:
        print("Couldn't fetch parent. Probably in root: "+context.user_data[CURRENT_FOLDER_KEY])
        print("Error :"+str(e))
        context.user_data[PARENT_FOLDER_ID_KEY] = None
        context.user_data[PARENT_FOLDER_KEY] = ""

    await change_folder(update, context)
    return SAVE_SELECT

async def new_folder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_folder_name = remove_emoji(update.message.text)
    translator = str.maketrans('','',string.punctuation)
    new_folder_name = new_folder_name.translate(translator)
    context.user_data[PARENT_FOLDER_ID_KEY], context.user_data[PARENT_FOLDER_KEY], context.user_data[CURRENT_FOLDER_ID_KEY], context.user_data[CURRENT_FOLDER_KEY] = context.bot_data[DRIVE_KEY].create_folder(new_folder_name, context.user_data)
    print("User {} ({}) created folder {} in {}".format(update.effective_user.first_name, update.effective_user.id, context.user_data[CURRENT_FOLDER_KEY], context.user_data[PARENT_FOLDER_KEY]))
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.id)

    await change_folder(update, context)
    return SAVE_SELECT

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for file in context.user_data[FILES_KEY]:
        try:os.remove(file)
        except:print("Couldn't delete file :", file)
    del context.user_data[FILES_KEY]
    await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=context.user_data[MSG_KEY].message_id, text="Cancelled. Please send image again to restart.", reply_markup=None)
    context.user_data[CURRENT_FOLDER_ID_KEY] = context.bot_data[DRIVE_KEY].root_folder
    context.user_data[CURRENT_FOLDER_KEY] = "root"
    context.user_data[PARENT_FOLDER_ID_KEY] = None
    context.user_data[PARENT_FOLDER_KEY] = ""    
    return ConversationHandler.END

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

async def getuserid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.effective_user.id)

async def restart_retrieve_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for file in context.user_data[FILES_KEY]:
        try:os.remove(file)
        except:print("Couldn't delete file :", file)
    del context.user_data[FILES_KEY]
    context.user_data[CURRENT_FOLDER_ID_KEY] = context.bot_data[DRIVE_KEY].root_folder
    context.user_data[CURRENT_FOLDER_KEY] = "root"
    context.user_data[PARENT_FOLDER_ID_KEY] = None
    context.user_data[PARENT_FOLDER_KEY] = ""
    await retrieve_image(update, context)
    return ConversationHandler.END

def main():
    drive = GoogleDrivito(DRIVE_ROOT_FOLDER)
    print(drive)

    with open(TOKEN_FILE) as f:
        token_file = json.load(f)
    token = token_file['drive']
    app = ApplicationBuilder().token(token).build()#.concurrent_updates(True).build() ###TEST CONCURRENT UPDATES. SI FONCTIONNE PAS, ESSAYER BLOCK=FALSE DANS IMAGE_CONV_HANDLER
    app.bot_data[DRIVE_KEY] = drive
    app.bot_data[ACTIF_KEY] = True

    image_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^Send to drive$"), change_folder)
            ],
        states={
            SAVE_SELECT:[
                CallbackQueryHandler(save_image, pattern="save_here"),
                CallbackQueryHandler(new_folder_req, pattern="new_folder"),
                CallbackQueryHandler(back_folder_req, pattern="back_folder"),
                CallbackQueryHandler(done, pattern="cancel"),
                CallbackQueryHandler(change_folder)
            ],
            FOLDER:[
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^(Done|Discard)$")), new_folder
                )
            ]
        },
        fallbacks=[
            MessageHandler(filters.Regex("^(Done|Discard)$"), done),
            MessageHandler(filters.PHOTO | filters.Document.IMAGE, restart_retrieve_image)
            ],
        block=False
    )
    app.add_handler(image_conv_handler)
    app.add_handler(CommandHandler(['newadmin', 'actif', 'inactif', 'removeadmin'], admin_command, filters=filters.COMMAND))
    app.add_handler(CommandHandler(['getuserid'], getuserid, filters=filters.COMMAND))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.IMAGE, retrieve_image, block=False))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
