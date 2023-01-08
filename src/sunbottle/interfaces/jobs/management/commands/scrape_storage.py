import datetime

from django.core.management.base import BaseCommand, CommandError

from sunbottle.application.scrape import scrape_storage
from sunbottle.data.electricity import models


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "battery",
            metavar="battery",
            type=str,
        )
        parser.add_argument("date", metavar="date", type=datetime.date.fromisoformat, nargs="?")

    def handle(self, *args, **options):
        """ """
        battery_name = options["battery"]
        date = options["date"]

        try:
            battery = models.Battery.objects.get(name=battery_name)
        except models.Battery.DoesNotExist:
            raise CommandError(f"Battery {battery_name} does not exist")

        scrape_storage(battery, date=date)
