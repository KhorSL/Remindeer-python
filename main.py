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
    update.message.reply_text('Start by selecting your bus stop by /set <busstopcode>')
    update.message.reply_text('For Example: /set 65191')
    update.message.reply_text('Or send your location to me! \U0001F609')

def help(bot, update):
    update.message.reply_text('Help is for the weak. Try harder \U0001F60A')

def remind(bot, update):
    input = update.message.text[8:]
    reminders = db.get_items()
    if input in reminders:
        pass
    else:
        db.add_item(input)
        reminders = db.get_items()
    message = "\n".join(reminders)
    update.message.reply_text(message)

def delete(bot, update):
    input = update.message.text[8:]
    try:
        db.delete_item(input)
        update.message.reply_text('`' + input + '`' + ' deleted')
    except KeyError:
        pass
    reminders = db.get_items()
    message = "\n".join(reminders)
    update.message.reply_text(message)

def error(bot, update, error):
    """Log Errors caused by Updates."""
    print ('Update "%s" caused error "%s"', update, error)
    logger.warning('Update "%s" caused error "%s"', update, error)

def main():
    """Deployment"""
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

    # """Local dev"""
    # db.setup()

    # # Create the Updater and pass it your bot's token.
    # # Make sure to set use_context=True to use the new context based callbacks
    # # Post version 12 this will no longer be necessary
    # updater = Updater(token)

    # # Get the dispatcher to register handlers
    # dp = updater.dispatcher

    # # on different commands - answer in Telegram
    # dp.add_handler(CommandHandler("start", start))
    # dp.add_handler(CommandHandler("help", help))
    # dp.add_handler(CommandHandler("remind", remind))
    # dp.add_handler(CommandHandler("delete", delete))

    # # on noncommand i.e message - echo the message on Telegram
    # # dp.add_handler(MessageHandler(Filters.text, echo))

    # # log all errors
    # dp.add_error_handler(error)

    # # Start the Bot
    # updater.start_polling()

    # # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # # SIGTERM or SIGABRT. This should be used most of the time, since
    # # start_polling() is non-blocking and will stop the bot gracefully.
    # updater.idle()

if __name__ == '__main__':
    print ('Bot is running')
    main()
    print ('Bot ending')