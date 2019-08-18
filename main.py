import os, requests, re, time, logging, textwrap

from datetime import datetime, timedelta
from configparser import ConfigParser
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, ParseMode
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackQueryHandler, ConversationHandler, RegexHandler
from apscheduler.schedulers.background import BackgroundScheduler

import keyboards.telegramcalendar as telegramcalendar
import config
import keyboards.reminder_alert as reminder_alert
import lib.emoji as emoji

from database import Database

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

# Database setup
db = Database()

# Scheduler setup
scheduler = BackgroundScheduler()

# Conversation Handler states
DATE, TIME = range(2)

# Messages
HELP_MESSAGE = 'To add a reminder: \n\n /remind [reminder] \n\n' \
                + 'To see all reminders: \n\n /list \n\n' \
                + 'To delete a reminder (index is the number seen after the /list command): \n\n /delete [index]'

'''Helper methods'''

def numbering_list(input_list):
    result = "%s Your current reminders:\n\n" % (emoji.MEMO)
    for i in range(len(input_list)):
        result = result + str(i+1) + ". " + input_list[i] + "\n"
    return result

def reply_user(update, reminders):
    if len(reminders) > 0:
        message = numbering_list(reminders)
        update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    else:
        message = "There are no reminders in your list."
        update.message.reply_text(message)

''' def truncate_string(str, num_char)

    This method truncate the string to the specified number of characters

    argument: (String, int)
    return: String

'''

def truncate_string(input_string, num_char):
    return input_string[:num_char] + (input_string[num_char:] and '...')

'''End of Helper Methods'''

''' Handlers '''

def callback_handler(bot, update):
    query = update.callback_query
    chat_id = query.message.chat_id
    message_id = query.message.message_id

    # Calendar
    if re.match("[\w-]+;[\d]{4};[\d]{1,2};[\d]{1,2}", query.data):
        selected, date = telegramcalendar.process_calendar_selection(bot, update)

        if selected:
            db.update_intermediate_reminder_date(date, chat_id)
            bot.send_message(text="You selected *%s* as the day of reminder. \n \n"
                "Please give me the time of reminder in 24 hours format (e.g. 23:59)" % (date.strftime("%d %b %Y, %a")), 
                chat_id=chat_id, reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.MARKDOWN)
            
            return TIME

    ''' Alert

        1. All Alert callback query data will contain the prefix `ALERT`.
        2. The callback query data paramaters are seperated by semi-colon `;`
        3. The reminder id should always be the first paramater

        4. The format of the callback query data will be as such:
            ALERT;[reminder id];[other parameter/actions]+
    '''
    snooze_cmd_match = re.match("ALERT;(.+)", query.data)
    if snooze_cmd_match:
        try:
            params = snooze_cmd_match.group(1)
            params_array = params.split(';')
            reminder_id = params_array[0]
            if db.reminder_exists(reminder_id):
                reminder_text = db.get_reminders_text_by_id(reminder_id)
                reminder_text = truncate_string(reminder_text, 20)

                if re.match("^(\d+);SNOOZE$", params):
                    bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id,
                        reply_markup=reminder_alert.create_snooze_keyboard(reminder_id))


                if re.match("^(\d+);(SNOOZE-BACK)$", params):
                    bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id,
                        reply_markup=reminder_alert.create_selection_keyboard(reminder_id))


                if re.match("^(\d+);SNOOZE;(\d+)$", params):
                    # params_arrary[reminder_id, 'SNOOZE', seconds]
                    snooze_timestamp = reminder_alert.process_snooze_selection(params_array[2])

                    db.update_reminder_date(snooze_timestamp, reminder_id)

                    # Conversion of default TZ for user readability
                    snooze_timestamp = snooze_timestamp.astimezone(config.DEFAULT_TZ)

                    bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=None)
                    bot.send_message(text="Snoozing \"%s\" until *%s*" % (reminder_text, snooze_timestamp.strftime("%d %b %Y, %a, %I:%M %p")),
                        chat_id=chat_id, parse_mode=ParseMode.MARKDOWN)


                if re.match("^(\d+);DELETE$", params):
                    bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, 
                        reply_markup=reminder_alert.create_confirmation_keyboard(reminder_id))


                if re.match("(\d+);(DELETE-Y|DELETE-N)", params):
                    if params_array[1] == "DELETE-Y":
                        db.delete_reminder_by_id(reminder_id, chat_id)
                        bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=None)
                        bot.send_message(text="`%s` deleted" % (reminder_text), chat_id=chat_id)
                    else:
                        bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id,
                            reply_markup=reminder_alert.create_selection_keyboard(reminder_id))
                                    
            else:
                bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=None)
                bot.send_message(text="Reminder does not exist.", chat_id=chat_id)

        except Exception as e:
            print (str(e))
            fast_clicker_message_excerpt = "exactly the same"
            if fast_clicker_message_excerpt in str(e): 
                bot.send_message(text="You are clicking too fast.", chat_id=chat_id)
            else:
                bot.send_message(text="You snooze, you lose.", chat_id=chat_id)


def start(bot, update):
    chat_id = update.message.chat_id
    update.message.reply_text('Hi there! %s \n\n %s' % (emoji.SMILING_EYES, HELP_MESSAGE))


def help(bot, update):
    update.message.reply_text('Sending help now %s \n\n %s' % (emoji.SMILING_EYES, HELP_MESSAGE))


def remind(bot, update):
    try:
        chat_id = update.message.chat_id
        input_reminder = re.match("\/[\w]+([@_\w]+|) (.+)", update.message.text).group(2)

        # Delete any leftover intermediate result for current chat
        db.delete_intermediate(chat_id)

        # Save intermediate result
        db.add_intermediate_reminder(input_reminder, chat_id)

        reminders = db.get_reminders_text(chat_id)
        update.message.reply_text("%s Please select a date %s" % (emoji.CALENDAR, emoji.CALENDAR),
            reply_markup=telegramcalendar.create_calendar())

        return DATE
    except AttributeError:
        update.message.reply_text("Please tell me something to remind you about.")
    except Exception:
        update.message.reply_text("Sorry an error had occurred, reminder was not added.")


def time(bot, update):
    user = update.message.from_user
    chat_id = update.message.chat_id
    time = update.message.text

    # Retrieve and remove user input from intermediate table
    intermediate = db.get_intermediate(chat_id)
    input_reminder = intermediate[2]

    # Creating datetime with default timezone
    date = str(intermediate[3]) + " " + time
    date = datetime.strptime(date, '%Y-%m-%d %H:%M')
    date = config.DEFAULT_TZ.localize(date)

    db.delete_intermediate(chat_id)

    db.add_reminder(input_reminder, chat_id, date)
    reminders = db.get_reminders_text(chat_id)

    confirmation_message = "Reminder set on " + date.strftime('%Y-%m-%d %H:%M')
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
    update.message.reply_text('Bye! I hope to receive a reminder some day.', reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def delete(bot, update):
    try:
        chat_id = update.message.chat_id
        reminders = db.get_reminders(chat_id)
        user_input = re.match("\/[\w]+([@_\w]+|) (.+)", update.message.text).group(2)
        index = int(user_input, 10)
        if index > 0:
            reminder_id = reminders[index - 1][0]
            db.delete_reminder_by_id(reminder_id, chat_id)
            update.message.reply_text('`' + reminders[index - 1][2] + '`' + ' deleted')
        else:
            update.message.reply_text('Please input a positive integer greater than zero.')
    except IndexError:
        update.message.reply_text('Index not found.')
    except ValueError:
        update.message.reply_text('Please input a positive integer greater than zero.')
    except AttributeError:
        update.message.reply_text('Please input a positive integer greater than zero.')
    except Exception:
        update.message.reply_text('An error occurred, reminder was not deleted.')

    reminders = db.get_reminders_text(chat_id)
    reply_user(update, reminders)


def list_all(bot, update):
    chat_id = update.message.chat_id
    reminders = db.get_reminders_text_and_time(chat_id)
    reminders_to_list = []
    for reminder in reminders:
        reminder_datetime = reminder[1].astimezone(config.DEFAULT_TZ)
        reminders_to_list.append("*" + reminder[0] + "*\n\n" + reminder_datetime.strftime("%d %b %Y, %a, %I:%M %p") + "\n\n")
    reply_user(update, reminders_to_list)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    print ('Update "%s" caused error "%s"', update, error)
    logger.warning('Update "%s" caused error "%s"', update, error)

''' End of Handlers'''

''' Jobs '''

def reminder_job():
    bot = Bot(config.TOKEN)
    print ("Getting reminders around %s" % (str(datetime.now(config.DEFAULT_TZ))))
    reminders_to_send = db.get_reminders_around_time(datetime.now())

    for reminder in reminders_to_send:
        # reminder(id, chat_id, text, time)
        chat_id = reminder[1]
        reminder_to_send = reminder[2]
        reminder_to_send = textwrap.fill(reminder_to_send, initial_indent='>>>  ', subsequent_indent='>>>  ', width=38)
        bot.send_message(text='%s Reminder Alert %s \n\n%s' % (emoji.CLOCK, emoji.CLOCK, reminder_to_send),
            chat_id=chat_id,
            reply_markup=reminder_alert.create_selection_keyboard(reminder[0]))


def ping():
    requests.get(config.APP_URL)

''' End of Jobs '''

def main():
    scheduler.add_job(ping, 'interval', minutes=5)
    scheduler.add_job(reminder_job, 'interval', minutes=1, start_date=datetime.now().replace(second=0, microsecond=0) + timedelta(minutes=1))
    scheduler.start()
    db.setup()
    updater = Updater(config.TOKEN)

    ''' Deployment '''
    updater.start_webhook(listen="0.0.0.0", port=config.PORT, url_path=config.TOKEN)
    
    dp = updater.dispatcher

    callback_query_handler = CallbackQueryHandler(callback_handler)

    # Add conversation handler with the states DATE and TIME
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('remind', remind)],

        states={
            DATE: [callback_query_handler],

            TIME: [RegexHandler('^(0[0-9]|1[0-9]|2[0-3]|[0-9]):[0-5][0-9]$', time)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("delete", delete))
    dp.add_handler(CommandHandler("list", list_all))
    dp.add_handler(callback_query_handler)

    # log all errors
    dp.add_error_handler(error)

    ''' Development '''
    # updater.start_polling()

    ''' Deployment '''
    updater.bot.set_webhook(config.APP_URL + config.TOKEN)

    updater.idle()


if __name__ == '__main__':
    print ('Bot is running')
    main()
    print ('Bot ending')
