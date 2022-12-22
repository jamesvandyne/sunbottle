from __future__ import annotations

import datetime
import decimal
from dataclasses import dataclass
from typing import Optional

from django.conf import settings
from django.utils import module_loading
from selenium import webdriver


@dataclass
class ConsumptionReading:
    occurred_at: datetime.datetime
    kwh: decimal.Decimal


class ConsumptionRetriever:
    def retrieve(
        self,
        browser: Optional[webdriver.Firefox] = None,
        date: Optional[datetime.date] = None,
    ) -> list[ConsumptionReading]:
        """
        Retrieve a list of generation readings.
        """
        raise NotImplementedError


def get_consumption_retriever() -> ConsumptionRetriever:
    return module_loading.import_string(settings.CONSUMPTION_RETRIEVER_CLASS)()
