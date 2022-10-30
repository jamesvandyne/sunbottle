from __future__ import annotations

import datetime
import decimal
from collections import deque
from typing import Optional, Union

from sunbottle.domain.electricity import buysell, generation, storage


def sharp_generation_to_reading(
    generation_data: list[float], date: Optional[datetime.date] = None
) -> list[generation.GenerationReading]:
    date = date or datetime.date.today()
    data = deque(generation_data)
    readings = []
    for hour in range(0, 24):
        for interval in [0, 15, 30, 45]:
            generated_at = datetime.datetime(
                year=date.year,
                month=date.month,
                day=date.day,
                hour=hour,
                minute=interval,
            )

            kwh = data.popleft()
            readings.append(generation.GenerationReading(occurred_at=generated_at, kwh=decimal.Decimal(str(kwh))))
    return readings


def sharp_storage_to_reading(
    storage_data: list[float], date: Optional[datetime.date] = None
) -> list[storage.StorageReading]:
    now = datetime.datetime.now()
    date = date or datetime.date.today()

    data = deque(storage_data)
    readings = []
    for hour in range(0, 24):
        for interval in [0, 15, 30, 45]:
            level_at = datetime.datetime(
                year=date.year,
                month=date.month,
                day=date.day,
                hour=hour,
                minute=interval,
            )
            # Skip if the data is speculative i.e. in the future.
            if level_at > now:
                continue
            charge_percent = data.popleft()
            readings.append(
                storage.StorageReading(
                    occurred_at=level_at,
                    charge=decimal.Decimal(str(charge_percent)),
                )
            )
    return readings


def sharp_buysell_to_reading(
    buysell_data: dict[str, list[float]], date: Optional[datetime.date] = None
) -> list[Union[buysell.BuyReading, buysell.SellReading]]:
    date = date or datetime.date.today()

    buy_data = deque(buysell_data["graphDataPurchase"])
    sell_data = deque(buysell_data["graphDataSelling"])
    readings = []

    for hour in range(0, 24):
        generated_at = datetime.datetime(
            year=date.year,
            month=date.month,
            day=date.day,
            hour=hour,
        )

        kwh = buy_data.popleft()
        readings.append(
            buysell.BuyReading(
                occurred_at=generated_at,
                kwh=decimal.Decimal(str(kwh)),
            )
        )

    for hour in range(0, 24):
        generated_at = datetime.datetime(
            year=date.year,
            month=date.month,
            day=date.day,
            hour=hour,
        )
        kwh = sell_data.popleft()
        readings.append(
            buysell.SellReading(
                occurred_at=generated_at,
                kwh=decimal.Decimal(str(kwh)),
            )
        )
    return readings
