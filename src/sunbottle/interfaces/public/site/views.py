import datetime

from django.conf import settings
from django.utils import timezone
from django.views import generic

from sunbottle.domain.electricity import queries


class Index(generic.TemplateView):
    template_name = "site/index.html"

    def setup(self, request, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        today = timezone.now().date()
        yesteday = today - datetime.timedelta(days=1)

        sold_kwh = queries.get_selling_for_date(today).normalize()
        total_kwh = queries.get_total_generation()
        context_data.update(
            {
                "date": today,
                "kwh": queries.get_generation_for_date(today).normalize(),
                "buying": queries.get_purchasing_for_date(today).normalize(),
                "selling": {
                    "kwh": sold_kwh,
                    "fit": settings.FIT,
                    "price": sold_kwh * settings.FIT,
                },
                "consumption": {
                    "yesterday": queries.get_consumption_for_date(yesteday).normalize(),
                    "today": queries.get_consumption_for_date(today).normalize(),
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
