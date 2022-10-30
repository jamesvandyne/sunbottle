import logging

from django.core import management
from uwsgidecorators import rbtimer

logger = logging.getLogger(__name__)

MINUTE = 60


@rbtimer(MINUTE * 30)
def scrape_everything(hoge) -> None:
    """
    Scrape new data every 30 minutes.
    """
    logger.info("Performing hourly scrape")
    logger.info("This gets passed %s", hoge)
    management.call_command("scrape_everything")
    logger.info("Finished hourly scrape")
