import os, requests, re
from configparser import ConfigParser
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

from database import Database

db = Database()

token = '895938816:AAEe0YkgUOjoOmQjvYEiErYBFxA9qhcChMY'
PORT = int(os.environ.get('PORT', '8443'))

def start(bot, update):
    chat_id = update.message.chat_id
    update.message.reply_text('Hi there! \U0001F60A')

def help(bot, update):
    update.message.reply_text('Help is for the weak. Try harder \U0001F60A')

def remind(bot, update):
    chat_id = update.message.chat_id
    input = update.message.text[8:]
    reminders = db.get_reminders(chat_id)
    if input in reminders:
        pass
    else:
        db.add_reminder(input, chat_id)
        reminders = db.get_reminders(chat_id)
    message = "\n".join(reminders)
    update.message.reply_text(message)

def delete(bot, update):
    input = update.message.text[8:]
    try:
        db.delete_reminder(input)
        update.message.reply_text('`' + input + '`' + ' deleted')
    except KeyError:
        pass
    reminders = db.get_reminders()
    message = "\n".join(reminders)
    update.message.reply_text(message)

def error(bot, update, error):
    """Log Errors caused by Updates."""
    print ('Update "%s" caused error "%s"', update, error)
    logger.warning('Update "%s" caused error "%s"', update, error)

def main():
    # """Deployment"""
    db.setup()
    updater = Updater(token)
    updater.start_webhook(listen="0.0.0.0",
                      port=PORT,
                      url_path=token)
    
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("remind", remind))
    dp.add_handler(CommandHandler("delete", delete))
	
    updater.bot.set_webhook("https://remindeer-bot.herokuapp.com/" + token)
    updater.idle()

    """Development"""
    # db.setup()

    # updater = Updater(token)

    # dp = updater.dispatcher

    # # on different commands - answer in Telegram
    # dp.add_handler(CommandHandler("start", start))
    # dp.add_handler(CommandHandler("help", help))
    # dp.add_handler(CommandHandler("remind", remind))
    # dp.add_handler(CommandHandler("delete", delete))

    # # log all errors
    # dp.add_error_handler(error)

    # # Start the Bot
    # updater.start_polling()

    # updater.idle()

if __name__ == '__main__':
    print ('Bot is running')
    main()
    print ('Bot ending')
