import os, requests, re
from configparser import ConfigParser
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler


token = <INSERT TOKEN>
PORT = int(os.environ.get('PORT', '8443'))

def start(bot,update):
    chat_id = update.message.chat_id
    update.message.reply_text('Hi there! \U0001F60A')
    update.message.reply_text('Start by selecting your bus stop by /set <busstopcode>')
    update.message.reply_text('For Example: /set 65191')
    update.message.reply_text('Or send your location to me! \U0001F609')

def main():
    updater.start_webhook(listen="0.0.0.0",
                      port=PORT,
                      url_path=token)
    
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start',start))
	
    updater.bot.set_webhook("https://kjb2.herokuapp.com/" + token)
    updater.idle()

if __name__ == '__main__':
    print ('Bot is running')
    main()
    print ('Bot ending')