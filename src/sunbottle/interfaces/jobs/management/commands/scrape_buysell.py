import datetime

from django.core.management.base import BaseCommand

from sunbottle.application.scrape import scrape_buysell


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("date", metavar="date", type=datetime.date.fromisoformat, nargs="?")

    def handle(self, *args, **options):
        """ """
        date = options["date"]
        scrape_buysell(date)
