import datetime

from django.core.management.base import BaseCommand, CommandError

from sunbottle.application.scrape import scrape_generation
from sunbottle.data.electricity import models


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "generator",
            metavar="generator",
            type=str,
        )
        parser.add_argument("date", metavar="date", type=datetime.date.fromisoformat, nargs="?")

    def handle(self, *args, **options):
        """ """
        generator_name = options["generator"]
        date = options["date"]

        try:
            generator = models.Generator.objects.get(name=generator_name)
        except models.Generator.DoesNotExist:
            raise CommandError(f"Generator {generator_name} does not exist")

        scrape_generation(generator)
