import datetime
import decimal

from django.db import models

from sunbottle.data.electricity import models as electricity_models


def get_total_generation() -> decimal.Decimal:
    return electricity_models.GenerationReading.objects.all().aggregate(total=models.Sum("kwh"))[
        "total"
    ] or decimal.Decimal("0.0")


def get_generation_for_date(date: datetime.date) -> decimal.Decimal:
    return electricity_models.GenerationReading.objects.filter(occurred_at__date=date).aggregate(
        total=models.Sum("kwh")
    )["total"] or decimal.Decimal("0.0")


def get_generation_series_for_date(date: datetime.date, exclude_future: bool = False) -> list[decimal.Decimal]:
    qs = electricity_models.GenerationReading.objects.filter(occurred_at__date=date).order_by("occurred_at")
    if exclude_future:
        now = datetime.datetime.now()
        qs = qs.exclude(occurred_at__gt=now)
    return qs.values_list("kwh", flat=True)


def get_generators() -> list[electricity_models.Generator]:
    return list(electricity_models.Generator.objects.all())


def get_batteries() -> list[electricity_models.Battery]:
    return list(electricity_models.Battery.objects.all())


def get_charge_for_battery(battery: electricity_models.Battery) -> decimal.Decimal:
    # There's a 15+ minute delay sometimes before the reading is live, so look 30 minutes into the
    # the past to prevent 0 readings from occurring often.
    half_hour_ago = datetime.datetime.now() - datetime.timedelta(minutes=30)
    return battery.level_readings.filter(occurred_at__lte=half_hour_ago).values_list(
        "charge_percent", flat=True
    ).order_by("occurred_at").last() or decimal.Decimal("0.0")


def get_purchasing_for_date(date: datetime.datetime) -> decimal.Decimal:
    return electricity_models.ElectricityPurchase.objects.filter(occurred_at__date=date).aggregate(
        total=models.Sum("kwh")
    )["total"] or decimal.Decimal("0.0")


def get_selling_for_date(date: datetime.datetime) -> decimal.Decimal:
    return electricity_models.ElectricitySale.objects.filter(occurred_at__date=date).aggregate(total=models.Sum("kwh"))[
        "total"
    ] or decimal.Decimal("0.0")


def get_coffee_cups_per_kwh(kwh: decimal.Decimal | None) -> decimal.Decimal:
    kwh = kwh or get_total_generation()
    watt_hour_per_cup = decimal.Decimal("20.667")
    return kwh_to_wh(kwh) / watt_hour_per_cup


def get_tesla_km_for_kwh(kwh: decimal.Decimal | None) -> decimal.Decimal:
    """
    Return the distance in km a Tesla Model 3 can be driven for the given kWh.
    """
    kwh = kwh or get_total_generation()
    combined_mild_weather_wh_per_km = decimal.Decimal("129.0")
    return kwh_to_wh(kwh) / combined_mild_weather_wh_per_km


def kwh_to_wh(kwh: decimal.Decimal) -> decimal.Decimal:
    return kwh * 1000
