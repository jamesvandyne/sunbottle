from __future__ import annotations

import datetime
import decimal
from dataclasses import dataclass
from typing import Optional, Union

from django.conf import settings
from django.utils import module_loading
from selenium import webdriver


@dataclass
class SellReading:
    occurred_at: datetime.datetime
    kwh: decimal.Decimal


@dataclass
class BuyReading:
    occurred_at: datetime.datetime
    kwh: decimal.Decimal


class BuySellRetriever:
    def retrieve(
        self,
        browser: Optional[webdriver.Firefox] = None,
        date: Optional[datetime.date] = None,
    ) -> list[Union[BuyReading, SellReading]]:
        """
        Retrieve a list of generation readings.
        """
        raise NotImplementedError


def get_buysell_retriever() -> BuySellRetriever:
    return module_loading.import_string(settings.BUYSELL_RETRIEVER_CLASS)()
