import arrow
from django.conf import settings
from django.views import generic

from sunbottle.domain.electricity import queries


class Index(generic.TemplateView):
    template_name = "site/index.html"

    def setup(self, request, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        today = arrow.now().floor("day")
        yesterday = today.shift(days=-1)

        sold_kwh = queries.get_selling_for_date(today.datetime).normalize()
        total_kwh = queries.get_total_generation()

        yesterday_consumption = queries.get_consumption_for_date(yesterday.datetime)
        yesterday_generation = queries.get_generation_for_date(yesterday.datetime)

        context_data.update(
            {
                "date": today,
                "buying": queries.get_purchasing_for_date(today.datetime).normalize(),
                "selling": {
                    "kwh": sold_kwh,
                    "fit": settings.FIT,
                    "price": sold_kwh * settings.FIT,
                },
                "generation": {
                    "yesterday": yesterday_generation.normalize(),
                    "today": queries.get_generation_for_date(today.datetime).normalize(),
                },
                "consumption": {
                    "yesterday": yesterday_consumption.normalize(),
                    "today": queries.get_consumption_for_date(today.datetime).normalize(),
                },
                "batteries": self.serialize_battery_summaries(),
                "all_time_kwh": total_kwh.normalize().quantize(10),
                "factoids": {
                    "coffee_total": queries.get_coffee_cups_per_kwh(total_kwh).quantize(10),
                    "tesla_km": queries.get_tesla_km_for_kwh(total_kwh).quantize(10),
                },
            }
        )
        return context_data

    def serialize_battery_summaries(self):
        summaries = []
        for battery in queries.get_batteries():
            summaries.append(
                {
                    "capacity": battery.capacity,
                    "current_charge": queries.get_charge_for_battery(battery).normalize(),
                }
            )
        return summaries


class Savings(generic.TemplateView):
    template_name = "site/savings.html"

    def get_context_data(self, **kwargs) -> dict:
        billing_periods = queries.get_billing_period_stats()
        lifetime_savings = sum(billing_period.total_savings for billing_period in billing_periods)
        return super().get_context_data(billing_periods=billing_periods, lifetime_savings=lifetime_savings)
