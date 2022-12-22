import datetime
from typing import Iterable

from django import http
from django.utils import timezone

from sunbottle.domain.electricity import queries

from . import serializers


def get_generation_line_graph(request: http.HttpRequest) -> http.JsonResponse:
    today = timezone.now().date()
    yesterday = today - datetime.timedelta(days=1)

    generation = queries.get_generation_series_for_date(yesterday)
    generation_today = queries.get_generation_series_for_date(today, exclude_future=True)
    data = serializers.LineGraphData(
        data={
            "labels": list(_get_15_minute_interval_labels()),
            "yesterday": {
                "label": "Yesterday",
                "data": list(generation),
            },
            "today": {"label": "Today", "data": list(generation_today)},
        }
    )
    if data.is_valid():
        return http.JsonResponse(data=data.validated_data)
    return http.JsonResponse(data={"error": data.errors})


def get_generation_summary(request: http.HttpRequest) -> http.JsonResponse:
    today = timezone.now().date()
    data = serializers.GenerationSummary(
        data={
            "total_generation": queries.get_total_generation(),
            "today_generation": queries.get_generation_for_date(today),
        }
    )
    if data.is_valid():
        return http.JsonResponse(data=data.validated_data)
    return http.JsonResponse(data={"error": data.errors})


def _get_15_minute_interval_labels() -> Iterable[str]:
    for hour in range(0, 24):
        for interval in [0, 15, 30, 45]:
            if interval == 0:
                yield str(hour)
            else:
                yield ""
