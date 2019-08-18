from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from datetime import datetime, timedelta

import lib.emoji as emoji

''' create_snooze_callback_data(time_item, reminder_id)
    
    argument: (datetime, int)
    return: String

    This function creates the callback data for the snooze keyboard buttons
'''

def create_snooze_callback_data(time_item, reminder_id):
    return "SNOOZE;" + str(reminder_id) + ";" + str(convert_seconds(time_item))


def convert_seconds(time_val):
    num = int(time_val[:-1])

    if time_val.endswith('m'):
        return num * 60
    elif time_val.endswith('h'):
        return num * 60 * 60
    elif time_val.endswith('d'):
        return num * 60 * 60 * 24
    elif time_val.endswith('w'):
        return num * 60 * 60 * 24 * 7

''' process_snooze_selection(snooze_seconds)
    
    argument: String
    return: datetime

    This function returns the addition of current time truncated to the latest minute with the snooze seconds
'''

def process_snooze_selection(snooze_seconds):
    return datetime.now().replace(second=0, microsecond=0) + timedelta(seconds=int(snooze_seconds))


def create_selection_keyboard(reminder_id):
    keyboard = []
    minute_row = ["1m", "5 m", "10 m", "15 m", "30 m"]
    hour_row = ["1 h", "2 h", "4 h", "8 h"]
    day_row = ["1 d", "2 d", "3 d"]
    week_row = ["1 w"]

    empty_row = [InlineKeyboardButton(" ", callback_data="IGNORE;%s" % (reminder_id))]

    delete_row = [InlineKeyboardButton("%s Delete" % (emoji.RUBBISH_BIN), callback_data="SNOOZE;%s;DELETE" % (reminder_id))]

    rows = [minute_row, hour_row, day_row, week_row]

    for row in rows:
        temp_row = []
        for item in row:
            temp_row.append(InlineKeyboardButton(item, callback_data=create_snooze_callback_data(item, reminder_id)))
        keyboard.append(temp_row)

    keyboard.append(empty_row)
    keyboard.append(delete_row)

    return InlineKeyboardMarkup(keyboard)


def create_confirmation_keyboard(reminder_id):
    keyboard = [
                [InlineKeyboardButton("Are you sure?", callback_data="IGNORE;%s" % (reminder_id))],
                [
                    InlineKeyboardButton(emoji.GREEN_TICK, callback_data="SNOOZE;%s;DELETE-Y" % (reminder_id)),
                    InlineKeyboardButton(emoji.RED_X_CROSS, callback_data="SNOOZE;%s;DELETE-N" % (reminder_id))
                ]
    ]

    return InlineKeyboardMarkup(keyboard)
