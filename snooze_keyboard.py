from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from datetime import datetime, timedelta
import calendar

def create_callback_data(time_item, reminder_id):
    return "SNOOZE;" + str(convert_seconds(time_item)) + ";" + str(reminder_id)


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


def process_snooze_selection(snooze_seconds, tz):
    return datetime.now(tz) + timedelta(seconds=int(snooze_seconds))


def create_keyboard(reminder_id):
    keyboard = []
    minute_row = ["5 m", "10 m", "15 m", "30 m"]
    hour_row = ["1 h", "2 h", "4 h", "8 h"]
    day_row = ["1 d", "2 d", "3 d"]
    week_row = ["1 w"]

    rows = [minute_row, hour_row, day_row, week_row]

    for row in rows:
        temp_row = []
        for item in row:
            temp_row.append(InlineKeyboardButton(item, callback_data=create_callback_data(item, reminder_id)))
        keyboard.append(temp_row)

    return InlineKeyboardMarkup(keyboard)
