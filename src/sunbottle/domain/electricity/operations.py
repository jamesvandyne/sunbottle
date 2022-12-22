from __future__ import annotations

from typing import Union

from django.db import transaction

from sunbottle.data.electricity import models
from sunbottle.domain.electricity import buysell, consumption, generation, storage


@transaction.atomic
def record_generation_readings(generator: models.Generator, readings: list[generation.GenerationReading]) -> None:
    """
    Save a series of generation readings
    """
    for reading in readings:
        models.GenerationReading.objects.update_or_create(
            generator=generator,
            occurred_at=reading.occurred_at,
            defaults={"kwh": reading.kwh},
        )


@transaction.atomic
def record_storage_readings(battery: models.Battery, readings: list[storage.StorageReading]) -> None:
    """
    Save a series of battery charge readings.
    """
    for reading in readings:
        models.BatteryLevelReading.objects.update_or_create(
            battery=battery,
            occurred_at=reading.occurred_at,
            defaults={"charge_percent": reading.charge},
        )


@transaction.atomic
def record_buy_sell_readings(readings: list[Union[buysell.BuyReading, buysell.SellReading]]) -> None:
    """
    Save a series of battery charge readings.
    """
    for reading in readings:
        model = models.ElectricityPurchase if isinstance(reading, buysell.BuyReading) else models.ElectricitySale
        model.objects.update_or_create(
            occurred_at=reading.occurred_at,
            defaults={"kwh": reading.kwh},
        )


@transaction.atomic
def record_consumption_readings(readings: list[consumption.ConsumptionReading]) -> None:
    """
    Save a series of consumption readings.
    """
    for reading in readings:
        models.ConsumptionReading.objects.update_or_create(occurred_at=reading.occurred_at, kwh=reading.kwh)
