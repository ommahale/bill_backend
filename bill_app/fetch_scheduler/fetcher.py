from apscheduler.schedulers.background import BackgroundScheduler

from bill_app.views import fetchCycle

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetchCycle, 'interval',days=1)
    scheduler.start()