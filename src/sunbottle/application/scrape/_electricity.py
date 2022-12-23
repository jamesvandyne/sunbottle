import datetime
import logging
from typing import Iterable, Optional

from django.conf import settings
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

from sunbottle.data.electricity import models as electricity_models
from sunbottle.domain.electricity import buysell, consumption, generation
from sunbottle.domain.electricity import operations as electricity_ops
from sunbottle.domain.electricity import queries, storage

logger = logging.getLogger(__name__)


def scrape_generation(generator: electricity_models.Generator, date: Optional[datetime.date] = None) -> None:
    """
    Scrapes generation data and associates it with a generator.
    """
    retriever = generation.get_generation_retriever()
    browser = _get_browser()

    # Record generation readings
    readings = retriever.retrieve(browser=browser, date=date)
    electricity_ops.record_generation_readings(generator, readings)

    browser.quit()


def scrape_storage(battery: electricity_models.Battery, date: Optional[datetime.date] = None) -> None:
    """
    Scrapes storage data and associates it with a battery.
    """
    retriever = storage.get_storage_retriever()
    browser = _get_browser()

    # Record battery level readings
    readings = retriever.retrieve(browser=browser, date=date)
    electricity_ops.record_storage_readings(battery, readings)

    browser.quit()


def scrape_buysell(date: Optional[datetime.date] = None) -> None:
    """
    Scrapes electricity buy/sell information.
    """
    retriever = buysell.get_buysell_retriever()
    browser = _get_browser()

    # Record generation readings
    readings = retriever.retrieve(browser=browser, date=date)
    electricity_ops.record_buy_sell_readings(readings)

    browser.quit()


def scrape_consumption(date: Optional[datetime.date] = None) -> None:
    """
    Scrapes consumption information.
    """
    retriever = consumption.get_consumption_retriever()
    browser = _get_browser()

    # Record consumption readings
    readings = retriever.retrieve(browser=browser, date=date)
    electricity_ops.record_consumption_readings(readings)

    _cleanup_browser(browser)


def scrape_consumption_range(start_date: datetime.date, end_date: datetime.date) -> None:
    """
    Scrapes consumption information.
    """
    retriever = consumption.get_consumption_retriever()
    browser = _get_browser()

    # Record consumption readings
    for date in _date_range(start_date, end_date):
        print(f"Scraping {date}")
        readings = retriever.retrieve(browser=browser, date=date)
        electricity_ops.record_consumption_readings(readings)

    _cleanup_browser(browser)


def scrape_everything(date: Optional[datetime.date]) -> None:
    """
    Scrapes all generation, storage, and buy sell data.
    """

    browser = _get_browser()

    try:
        _scrape_everything(browser, date)
    except Exception as e:
        logger.exception("Error scarping %s" % e)

    _cleanup_browser(browser)


def _scrape_everything(browser: webdriver.Firefox, date: Optional[datetime.date]) -> None:
    generation_retriever = generation.get_generation_retriever()
    storage_retriever = storage.get_storage_retriever()
    buysell_retriever = buysell.get_buysell_retriever()
    consumption_retreiver = consumption.get_consumption_retriever()

    # Record generation readings
    for generator in queries.get_generators():
        generation_readings = generation_retriever.retrieve(browser=browser, date=date)
        electricity_ops.record_generation_readings(generator, generation_readings)

    for battery in queries.get_batteries():
        # Record battery level readings
        readings = storage_retriever.retrieve(browser=browser, date=date)
        electricity_ops.record_storage_readings(battery, readings)

    buysell_readings = buysell_retriever.retrieve(browser=browser, date=date)
    electricity_ops.record_buy_sell_readings(buysell_readings)

    consumption_readings = consumption_retreiver.retrieve(browser=browser, date=date)
    electricity_ops.record_consumption_readings(consumption_readings)


def _cleanup_browser(browser: webdriver.Firefox) -> None:
    """
    Close the browser and quit the web driver
    """
    browser.close()
    browser.quit()


def _get_browser() -> webdriver.Firefox:
    service = FirefoxService(executable_path=GeckoDriverManager(path=settings.WEBDRIVER_INSTALL_PATH).install())
    driver = webdriver.Firefox(service=service)
    return driver


def _date_range(start_date: datetime.date, end_date: datetime.date) -> Iterable[datetime.date]:
    for n in range(int((end_date - start_date).days)):
        yield start_date + datetime.timedelta(days=n)
