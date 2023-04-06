from django.apps import AppConfig


class BillAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bill_app'
    def ready(self) -> None:
        print('Starting scheduler...')
        print('Fetch cycle in 12hrs')
        from .fetch_scheduler import fetcher
        fetcher.start()
