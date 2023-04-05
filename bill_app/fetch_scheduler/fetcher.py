from apscheduler.schedulers.background import BackgroundScheduler

from bill_app.views import fetchCycle

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetchCycle, 'interval',days=5)
    scheduler.start()