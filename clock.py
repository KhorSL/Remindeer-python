from apscheduler.schedulers.blocking import BlockingScheduler
from telegram import Bot
from database import Database
from datetime import datetime

token = '895938816:AAEe0YkgUOjoOmQjvYEiErYBFxA9qhcChMY'

# def send_reminder():
#   db = Database()
#   bot = Bot(token)
#   reminders_to_send = db.get_reminders_to_send(datetime.now())

#   for reminder in reminders_to_send:
#       chat_id = reminder[1]
#       reminder_to_send = reminder[2]
#       bot.send_message(text='\u23F0 Reminder Alert \u23F0 \n\n' + reminder_to_send, chat_id=chat_id)

# def add_reminder_job(date):
#   scheduler = BlockingScheduler()
#   scheduler.start()
#   scheduler.add_job(send_reminder, 'date', run_date=date+":00")

if __name__ == "__main__":
    scheduler = BlockingScheduler()

    @scheduler.scheduled_job('interval', minutes=60)
    def timed_job():
        print('Scheduler is alive')

    @scheduler.scheduled_job('cron', day_of_week='mon-fri', hour=9)
    def scheduled_job():
      db = Database()
      bot = Bot(token)
      reminders_to_send = db.get_all_reminders()

      for reminder in reminders_to_send:
          chat_id = reminder[1]
          reminder_to_send = reminder[2]
          bot.send_message(text='\u23F0 Reminder Alert \u23F0 \n\n' + reminder_to_send, chat_id=chat_id)

    try:
        scheduler.start()
    except KeyboardInterrupt:
        pass
