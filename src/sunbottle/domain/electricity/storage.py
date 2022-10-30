from __future__ import annotations

import datetime
import decimal
from dataclasses import dataclass
from typing import Optional

from django.conf import settings
from django.utils import module_loading
from selenium import webdriver


@dataclass
class StorageReading:
    occurred_at: datetime.datetime
    charge: decimal.Decimal


class StorageRetriever:
    def retrieve(
        self,
        browser: Optional[webdriver.Firefox] = None,
        date: Optional[datetime.date] = None,
    ) -> list[StorageReading]:
        """
        Retrieve a list of generation readings.
        """
        raise NotImplementedError


def get_storage_retriever() -> StorageRetriever:
    return module_loading.import_string(settings.STORAGE_RETRIEVER_CLASS)()
