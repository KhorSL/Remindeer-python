import os, requests, re, time, logging

from datetime import datetime, timedelta
from configparser import ConfigParser
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler, RegexHandler
from apscheduler.schedulers.background import BackgroundScheduler

import telegramcalendar

from database import Database

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

# Database setup
db = Database()

# Scheduler setup
scheduler = BackgroundScheduler()

# Configs
token = '895938816:AAEe0YkgUOjoOmQjvYEiErYBFxA9qhcChMY'
PORT = int(os.environ.get('PORT', '8443'))
app_url = "https://remindeer-bot.herokuapp.com/"

# Conversation Handler states
DATE, TIME = range(2)

# Helper methods
def numbering_list(input_list):
    result = "\U0001F4DD Your current reminders:\n\n"
    for i in range(len(input_list)):
        result = result + str(i+1) + ". " + input_list[i] + "\n"
    return result

def reply_user(update, reminders):
    if len(reminders) > 0:
        message = numbering_list(reminders)
        update.message.reply_text(message)
    else:
        message = "There are no reminders in your list."
        update.message.reply_text(message)

def date_handler(bot, update):
    query = update.callback_query

    selected, date = telegramcalendar.process_calendar_selection(bot, update)

    if selected:
        chat_id = query.message.chat_id
        db.update_intermediate_reminder_date(date, chat_id)
        bot.send_message(text="You selected %s as the day of reminder. \n \n"
            "Please give me the time of reminder in 24 hours format (e.g. 23:59)" % (date.strftime("%d/%m/%Y")), 
            chat_id=chat_id, reply_markup=ReplyKeyboardRemove())
        
        return TIME

def start(bot, update):
    chat_id = update.message.chat_id
    update.message.reply_text('Hi there! \U0001F60A')
    update.message.reply_text('To add a reminder: \n\n /remind [reminder]')
    update.message.reply_text('To see all reminders: \n\n /list')
    update.message.reply_text('To delete a reminder (index is the number seen after the /list command): \n\n /delete [index]')

def help(bot, update):
    update.message.reply_text('Help is for the weak. Try harder \U0001F60A')
    update.message.reply_text('To add a reminder: \n\n /remind [reminder]')
    update.message.reply_text('To see all reminders: \n\n /list')
    update.message.reply_text('To delete a reminder (index is the number seen after the /list command): \n\n /delete [index]')

def remind(bot, update):
    chat_id = update.message.chat_id
    input_reminder = update.message.text[8:]

    # Delete any leftover intermediate result for current chat
    db.delete_intermediate(chat_id)

    # Save intermediate result
    db.add_intermediate_reminder(input_reminder, chat_id)

    reminders = db.get_reminders_text(chat_id)
    if input in reminders:
        pass
    else:
        update.message.reply_text("\U0001F4C5 Please select a date \U0001F4C5", reply_markup=telegramcalendar.create_calendar())

    return DATE

def time(bot, update):
    user = update.message.from_user
    chat_id = update.message.chat_id
    time = update.message.text

    # Retrieve and remove user input from intermediate table
    intermediate = db.get_intermediate(chat_id)
    input_reminder = intermediate[2]
    date = str(intermediate[3]) + " " + time
    db.delete_intermediate(chat_id)

    db.add_reminder(input_reminder, chat_id, date)
    reminders = db.get_reminders_text(chat_id)

    # scheduler.add_job(tick, 'date', run_date=date+":00")

    # add_reminder_job(date)

    confirmation_message = "Reminder set on " + date
    bot.send_message(text=confirmation_message, chat_id=chat_id, reply_markup=ReplyKeyboardRemove())

    if len(reminders) > 0:
        message = numbering_list(reminders)
        bot.send_message(text=message, chat_id=chat_id, reply_markup=ReplyKeyboardRemove())
    else:
        message = "There are no reminders in your list."
        bot.send_message(text=message, chat_id=chat_id, reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END    

def cancel(bot, update):
    user = update.message.from_user
    update.message.reply_text('Bye! I hope to receieve a reminder some day.', reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def delete(bot, update):
    chat_id = update.message.chat_id
    reminders = db.get_reminders(chat_id)
    input = update.message.text[8:]
    index = int(input, 10)
    
    reminder_id = reminders[index - 1][0]

    try:
        db.delete_reminder_by_id(input, chat_id)
        # update.message.reply_text('`' + input + '`' + ' deleted')
        update.message.reply_text('`' + reminders[index - 1][2] + '`' + ' deleted')
    except KeyError:
        pass
    reminders = db.get_reminders_text(chat_id)
    reply_user(update, reminders)

def list_all(bot, update):
    chat_id = update.message.chat_id
    reminders = db.get_reminders_text(chat_id)
    reply_user(update, reminders)

def error(bot, update, error):
    """Log Errors caused by Updates."""
    print ('Update "%s" caused error "%s"', update, error)
    logger.warning('Update "%s" caused error "%s"', update, error)

def tick():
    bot = Bot(token)
    reminders_to_send = db.get_reminders_to_send(datetime.now())

    for reminder in reminders_to_send:
        chat_id = reminder[1]
        reminder_to_send = reminder[2]
        bot.send_message(text='\u23F0 Reminder Alert \u23F0 \n\n' + reminder_to_send, chat_id=chat_id)

def reminder_job():
    bot = Bot(token)
    reminders_to_send = db.get_reminders_around_time(datetime.now() + timedelta(hours=8))

    for reminder in reminders_to_send:
        chat_id = reminder[1]
        reminder_to_send = reminder[2]
        bot.send_message(text='\u23F0 Reminder Alert \u23F0 \n\n' + reminder_to_send, chat_id=chat_id)

def ping():
    requests.get(app_url)

def main():
    """Deployment"""
    scheduler.add_job(ping, 'interval', minutes=5)
    scheduler.start()
    db.setup()
    updater = Updater(token)
    updater.start_webhook(listen="0.0.0.0",
                      port=PORT,
                      url_path=token)
    
    dp = updater.dispatcher

    # Add conversation handler with the states DATE and TIME
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('remind', remind)],

        states={
            DATE: [CallbackQueryHandler(date_handler)],

            TIME: [RegexHandler('^(0[0-9]|1[0-9]|2[0-3]|[0-9]):[0-5][0-9]$', time)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("delete", delete))
    dp.add_handler(CommandHandler("list", list_all))
	
    # log all errors
    dp.add_error_handler(error)

    updater.bot.set_webhook(app_url + token)
    updater.idle()

    """Development"""
    # db.setup()

    # updater = Updater(token)
    
    # dp = updater.dispatcher

    # # Add conversation handler with the states DATE and TIME
    # conv_handler = ConversationHandler(
    #     entry_points=[CommandHandler('remind', remind)],

    #     states={
    #         DATE: [CallbackQueryHandler(date_handler)],

    #         TIME: [RegexHandler('^(0[0-9]|1[0-9]|2[0-3]|[0-9]):[0-5][0-9]$', time)]
    #     },

    #     fallbacks=[CommandHandler('cancel', cancel)]
    # )

    # dp.add_handler(conv_handler)

    # # on different commands - answer in Telegram
    # dp.add_handler(CommandHandler("start", start))
    # dp.add_handler(CommandHandler("help", help))
    # dp.add_handler(CommandHandler("delete", delete))
    # dp.add_handler(CommandHandler("list", list_all))

    # # log all errors
    # dp.add_error_handler(error)

    # # Start the Bot
    # updater.start_polling()

    # updater.idle()

if __name__ == '__main__':
    print ('Bot is running')
    main()
    print ('Bot ending')
