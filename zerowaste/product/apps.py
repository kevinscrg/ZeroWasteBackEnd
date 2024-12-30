from datetime import date
import sys
from django.apps import AppConfig
import logging


class ProductConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'product'
    
    def ready(self):
        if "zerowaste.asgi:application" in sys.argv:
            from product.services.tasks import schedule_daily_emails  
            today = date.today()
            logger = logging.getLogger("daphne")
            logger.info( f"Scheduling daily emails for {today}...")
            schedule_daily_emails.delay()
            return super().ready()
