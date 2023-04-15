from apscheduler.schedulers.background import BackgroundScheduler

from bill_app.views import fetchCycle

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetchCycle, 'interval',hours=12,start_date='2023-04-04 00:00:00',timezone='Asia/Kolkata')
    scheduler.start()