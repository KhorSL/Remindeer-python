from apscheduler.schedulers.blocking import BlockingScheduler
from main import reminder_job

def job():
    reminder_job()

sched = BlockingScheduler()

sched.add_job(job, 'interval', minutes=1)

sched.start()
