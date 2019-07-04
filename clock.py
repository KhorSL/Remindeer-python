from apscheduler.schedulers.blocking import BlockingScheduler
from main import reminder_job

def job():
    reminder_job()

sched = BlockingScheduler()

sched.start()

sched.add_job(job, 'interval', minutes=5)
