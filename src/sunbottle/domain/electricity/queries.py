import datetime
import decimal
from dataclasses import dataclass
from typing import Iterable

import qsstats
from dateutil import rrule
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import models
from django.db.models import Sum

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
    half_hour_ago = datetime.datetime.now() - datetime.timedelta(minutes=31)
    return battery.level_readings.filter(occurred_at__lt=half_hour_ago).values_list(
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


def get_consumption_for_date(date: datetime.date) -> decimal.Decimal:
    return electricity_models.ConsumptionReading.objects.filter(occurred_at__date=date).aggregate(
        total=models.Sum("kwh")
    )["total"] or decimal.Decimal("0.0")


@dataclass
class BillingPeriodStats:
    start_at: datetime.datetime
    end_at: datetime.datetime
    total_consumption: decimal.Decimal
    total_generation: decimal.Decimal
    total_sold: decimal.Decimal

    total_cost: decimal.Decimal
    actual_cost: decimal.Decimal
    sold_price: decimal.Decimal

    generation_savings: decimal.Decimal
    sold_price: decimal.Decimal
    total_savings: decimal.Decimal

    daily_data: dict


def get_fuel_adjustment_charge(date: datetime.date) -> decimal.Decimal:
    """
    Return the fuel adjustment cost for a given period.

    If not found, return the last fuel adjustment charge before the given date.
    """
    try:
        return settings.FUEL_ADJUSTMENT_CHARGES[date]
    except KeyError:
        last_adjustment_charge = _get_date_before_date(date, settings.FUEL_ADJUSTMENT_CHARGES.keys())
        return settings.FUEL_ADJUSTMENT_CHARGES[last_adjustment_charge]


def get_renewable_charge(date: datetime.date) -> decimal.Decimal:
    """
    Return the renewable charge for a given period.

    If not found, return the last renewable charge before the given date.
    """
    try:
        return settings.RENEWABLE_ENERGY_CHARGES[date]
    except KeyError:
        last_renewable_charge = _get_date_before_date(date, settings.RENEWABLE_ENERGY_CHARGE.keys())
        return settings.RENEWABLE_ENERGY_CHARGES[last_renewable_charge]


def get_tariff_for_date(date: datetime.date) -> dict[tuple[int, int | None]]:
    """
    Return the tariff that should be used to calculate kWh costs for a given period.
    """
    try:
        return settings.AGREEMENTS[date]
    except KeyError:
        last_agreement_date = _get_date_before_date(date, settings.AGREEMENTS.keys())
        return settings.AGREEMENTS[last_agreement_date]


def get_billing_period_ranges(start_at: datetime.date | None = None) -> Iterable[tuple[datetime.date, datetime.date]]:
    period_start_date = start_at or settings.FIRST_BILLING_PERIOD_START
    period_end_date = period_start_date + relativedelta(months=1, days=-1)
    today = datetime.date.today()
    while True:
        if period_start_date < today:

            yield period_start_date, period_end_date
        else:
            break
        period_start_date = period_end_date + relativedelta(days=1)
        period_end_date = period_start_date + relativedelta(months=1, days=-1)


def get_base_cost(billing_period_start: datetime.date, kwh: decimal.Decimal) -> decimal.Decimal:
    """
    Return the base cost of the electricity for the total amount of kWh according to the agreement for that time.
    """
    tariff = get_tariff_for_date(billing_period_start)
    total_cost = decimal.Decimal("0.0")
    total_kwh = kwh

    for (tier_min, tier_max), price_per_kwh in reversed(tariff.items()):
        if tier_min > total_kwh:
            # Didn't use enough to reach this tier, skip calculations
            continue
        tier_max_kwh = tier_max if tier_max else total_kwh
        tier_kwh = int(tier_max_kwh) - tier_min
        tier_cost = tier_kwh * price_per_kwh
        total_cost += tier_cost
    return total_cost


def get_total_cost(billing_period_start_date: datetime.date, kwh: decimal.Decimal) -> decimal.Decimal:
    """
    Get the fully loaded cost for the given kWh amount.
    """
    fuel_adjustment_cost = get_fuel_adjustment_charge(billing_period_start_date)
    renewable_cost = get_renewable_charge(billing_period_start_date)

    return sum([get_base_cost(billing_period_start_date, kwh), (fuel_adjustment_cost * kwh), (renewable_cost * kwh)])


def get_sold_price(kwh: decimal.Decimal) -> decimal.Decimal:
    return kwh * settings.FIT


def get_billing_period_stats() -> list[BillingPeriodStats]:
    generation = electricity_models.GenerationReading.objects.all()
    consumption = electricity_models.ConsumptionReading.objects.all()
    buying = electricity_models.ElectricityPurchase.objects.all()
    selling = electricity_models.ElectricitySale.objects.all()

    generation_stats = qsstats.QuerySetStats(generation, date_field="occurred_at", aggregate=Sum("kwh"))
    consumption_stats = qsstats.QuerySetStats(consumption, date_field="occurred_at", aggregate=Sum("kwh"))
    buying_stats = qsstats.QuerySetStats(buying, date_field="occurred_at", aggregate=Sum("kwh"))
    selling_stats = qsstats.QuerySetStats(selling, date_field="occurred_at", aggregate=Sum("kwh"))
    billing_periods: list[BillingPeriodStats] = []
    for period_start, period_end in get_billing_period_ranges():

        start_at = datetime.datetime(period_start.year, period_start.month, period_start.day)
        end_at = datetime.datetime(period_end.year, period_end.month, period_end.day, hour=23, minute=59, second=59)

        generation_for_period: dict[datetime.date, decimal.Decimal] = dict(
            generation_stats.time_series(start_at, end_at)
        )
        consumption_for_period: dict[datetime.date, decimal.Decimal] = dict(
            consumption_stats.time_series(start_at, end_at)
        )
        bought_for_period: dict[datetime.date, decimal.Decimal] = dict(buying_stats.time_series(start_at, end_at))
        sold_for_period: dict[datetime.date, decimal.Decimal] = dict(selling_stats.time_series(start_at, end_at))

        total_generation = sum(generation_for_period.values()) or decimal.Decimal("0.00")
        total_sold = sum(sold_for_period.values()) or decimal.Decimal("0.00")

        # Costing

        total_consumption = sum(consumption_for_period.values()) or decimal.Decimal("0.00")
        total_cost = get_total_cost(period_start, total_consumption)

        total_bought = sum(bought_for_period.values()) or decimal.Decimal("0.00")
        actual_cost = get_total_cost(period_start, total_bought)
        sold_price = get_sold_price(total_sold)

        generation_savings = decimal.getcontext().subtract(total_cost, actual_cost)
        total_savings = generation_savings + sold_price

        rows = dict()
        for date in rrule.rrule(rrule.DAILY, start_at, until=end_at):
            rows[date] = dict(
                generation=decimal.Decimal(generation_for_period.get(date, "0")),
                consumption=decimal.Decimal(consumption_for_period.get(date, "0")),
                bought=decimal.Decimal(bought_for_period.get(date, "0")),
                sold=decimal.Decimal(sold_for_period.get(date, "0")),
            )

        billing_periods.append(
            BillingPeriodStats(
                start_at=start_at,
                end_at=end_at,
                total_consumption=total_consumption,
                total_generation=total_generation,
                total_cost=total_cost.quantize(10, rounding=decimal.ROUND_05UP),
                actual_cost=actual_cost.quantize(10, rounding=decimal.ROUND_05UP),
                total_sold=total_sold.quantize(10, rounding=decimal.ROUND_05UP),
                sold_price=sold_price.quantize(10, rounding=decimal.ROUND_05UP),
                generation_savings=generation_savings.quantize(10, rounding=decimal.ROUND_05UP),
                total_savings=total_savings.quantize(10, rounding=decimal.ROUND_05UP),
                daily_data=rows,
            )
        )
    return billing_periods


def _get_date_before_date(target_date: datetime.date, dates: Iterable[datetime.date]) -> datetime.date:
    return sorted(filter(lambda start_date: start_date <= target_date, dates))[-1]
