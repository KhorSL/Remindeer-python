from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from datetime import datetime, timedelta

import lib.emoji as emoji

def create_date_shortcut_keyboard():
    today_date_time = datetime.today()
    keyboard = [
        [
            InlineKeyboardButton("Today", callback_data="DAY;" + today_date_time.strftime("%Y;%-m;%-d")),
            InlineKeyboardButton("Tomorrow", callback_data="DAY;" + (today_date_time +  timedelta(days=1)).strftime("%Y;%-m;%-d")),
        ],
        
        [
            InlineKeyboardButton("2 d", callback_data="DAY;" + (today_date_time +  timedelta(days=2)).strftime("%Y;%-m;%-d")),
            InlineKeyboardButton("3 d", callback_data="DAY;" + (today_date_time +  timedelta(days=3)).strftime("%Y;%-m;%-d")),
            InlineKeyboardButton("1 w", callback_data="DAY;" + (today_date_time +  timedelta(days=7)).strftime("%Y;%-m;%-d"))
        ],
        
        [
            InlineKeyboardButton("Open Calendar " + emoji.CALENDAR, callback_data="SELECT;CALENDAR")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
