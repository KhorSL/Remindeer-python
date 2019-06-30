import os, requests, re
from configparser import ConfigParser
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

from database import Database

import telegramcalendar
from telegram import ReplyKeyboardRemove

import re

db = Database()

token = '895938816:AAEe0YkgUOjoOmQjvYEiErYBFxA9qhcChMY'
PORT = int(os.environ.get('PORT', '8443'))

# Helper methods
def numbering_list(input_list):
    result = ""
    for i in range(len(input_list)):
        result = result + str(i+1) + ". " + input_list[i] + "\n"
    return result

def reply_user(update, reminders):
    if len(reminders) > 0:
        # message = "\n".join(reminders)
        message = numbering_list(reminders)
        update.message.reply_text(message)
    else:
        message = "There are no reminders in your list."
        update.message.reply_text(message)

def inline_handler(bot, update):
    query = update.callback_query

    if re.match(r"DAY;\d+;\d+;\d+", query.data):
        selected, date = telegramcalendar.process_calendar_selection(bot, update)

        if selected:
            chat_id = query.message.chat_id
            bot.send_message(text="You selected %s" % (date.strftime("%d/%m/%Y")), chat_id=chat_id, reply_markup=ReplyKeyboardRemove())
            
            # Retrieve and remove user input from intermediate table
            input_reminder = db.get_intermediate(chat_id)[0]
            db.delete_intermediate(chat_id)

            db.add_reminder(input_reminder, chat_id, date)
            reminders = db.get_reminders(chat_id)
            
            if len(reminders) > 0:
                message = numbering_list(reminders)
                bot.send_message(text=message, chat_id=chat_id)
            else:
                message = "There are no reminders in your list."
                bot.send_message(text=message, chat_id=chat_id)


def start(bot, update):
    chat_id = update.message.chat_id
    update.message.reply_text('Hi there! \U0001F60A')

def help(bot, update):
    update.message.reply_text('Help is for the weak. Try harder \U0001F60A')

def remind(bot, update):
    chat_id = update.message.chat_id
    input_reminder = update.message.text[8:]

    # Delete any leftover intermediate result for current chat
    db.delete_intermediate(chat_id)

    # Save intermediate result
    db.add_intermediate(input_reminder, chat_id)

    reminders = db.get_reminders(chat_id)
    if input in reminders:
        pass
    else:
        update.message.reply_text("Please select a date: ", reply_markup=telegramcalendar.create_calendar())

def delete(bot, update):
    chat_id = update.message.chat_id
    input = update.message.text[8:]
    try:
        db.delete_reminder(input, chat_id)
        update.message.reply_text('`' + input + '`' + ' deleted')
    except KeyError:
        pass
    reminders = db.get_reminders(chat_id)
    reply_user(update, reminders)

def list_all(bot, update):
    chat_id = update.message.chat_id
    reminders = db.get_reminders(chat_id)
    reply_user(update, reminders)

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
    dp.add_handler(CommandHandler("list", list_all))
    dp.add_handler(CallbackQueryHandler(inline_handler))
	
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
    # dp.add_handler(CommandHandler("list", list_all))
    # dp.add_handler(CallbackQueryHandler(inline_handler))

    # # log all errors
    # dp.add_error_handler(error)

    # # Start the Bot
    # updater.start_polling()

    # updater.idle()

if __name__ == '__main__':
    print ('Bot is running')
    main()
    print ('Bot ending')
