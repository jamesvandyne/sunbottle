import datetime

from django.core.management.base import BaseCommand

from sunbottle.application.scrape import scrape_consumption_range


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("start", metavar="start", type=datetime.date.fromisoformat, nargs="?")
        parser.add_argument("end", metavar="end", type=datetime.date.fromisoformat, nargs="?")

    def handle(self, *args, **options):
        """ """
        scrape_consumption_range(options["start"], options["end"])
