from __future__ import annotations

import datetime
import decimal
from dataclasses import dataclass
from typing import Optional

from django.conf import settings
from django.utils import module_loading
from selenium import webdriver


@dataclass
class GenerationReading:
    occurred_at: datetime.datetime
    kwh: decimal.Decimal


class GenerationRetriever:
    def retrieve(
        self,
        browser: Optional[webdriver.Firefox] = None,
        date: Optional[datetime.date] = None,
    ) -> list[GenerationReading]:
        """
        Retrieve a list of generation readings.
        """
        raise NotImplementedError


def get_generation_retriever() -> GenerationRetriever:
    return module_loading.import_string(settings.GENERATION_RETRIEVER_CLASS)()
